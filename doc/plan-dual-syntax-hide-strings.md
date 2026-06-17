# Plan: Dual-syntax support + marker hide-list generation for NTTT

## Context

NTTT ("Nina's Translation Tidy-up Tool") cleans up Crowdin-translated Raspberry Pi
project content. Today it:

- Runs **only on the download side** (the `nttt-processing.yml` step), normalising and
  reverting translated content after it comes back from Crowdin.
- Understands **only the legacy `kramdown-rpf` syntax** (`--- task ---`, `--- hint ---`,
  `--- /no-print ---`, …) — see [cleanup_sections.py](nttt/cleanup_sections.py).

Two things are changing:

1. A **new "Raspberry Flavoured Markdown" (RFM)** syntax is being introduced — GFM
   blockquote alerts (`> [!TASK]`, `> [!HINT]`, `> [!ACCORDION] Title`, `> [!NOPRINT]`,
   page breaks, fenced-code attributes). NTTT must support **both** syntaxes, and **a single
   file may mix the two** (confirmed with the user).
2. Marker hiding (so translators never translate structural markers) is currently done by a
   brittle `grep` pipeline in the content repos' `hide-strings.yml`. We are moving that logic
   into NTTT (branch name: `nttt-no-hide-strings`). **NTTT will generate the Crowdin hide-list**
   (the chosen mechanism); markers stay in the files, and the existing download-side
   fix/revert pipeline puts any mangled markers back to their English form.

**Decisions confirmed with the user:**
- Mechanism = **generate Crowdin hide-list** (markers are hidden in Crowdin, not stripped from files).
- Marker set = **configurable** (ship a sensible default = all structural markers, editable by non-devs).
- Files **may mix** legacy + RFM markers — handle both within one file.
- Deliver **NTTT tool changes + example workflow ymls**.

**Outcome:** NTTT supports legacy and RFM content, owns the hide-list generation (retiring the
grep in `hide-strings.yml`), and the marker set lives in one declarative data file that a
non-Python maintainer can edit.

---

## Design overview — a single declarative marker registry

The centrepiece (and the answer to "modular, maintainable by non-Python devs") is **one data
file** describing every block type and its legacy + RFM spellings, plus whether it should be
hidden. All code reads from it; adding/removing a block type or toggling hiding is a YAML edit,
no Python.

`nttt/markers.yml` (ruamel.yaml is already a dependency):

```yaml
# Edit this file to add/remove block types or change what gets hidden from translators.
# 'hide: true' => NTTT lists this marker's strings for Crowdin to hide.
markers:
  - name: task
    hide: true
    legacy: { open: "--- task ---", close: "--- /task ---" }
    rfm:    { alert: "[!TASK]" }
  - name: hint
    hide: true
    legacy: { open: "--- hint ---", close: "--- /hint ---" }
    rfm:    { alert: "[!HINT]" }
  - name: collapse           # RFM calls this ACCORDION; title is translatable
    hide: true
    legacy: { open: "--- collapse ---", close: "--- /collapse ---" }
    rfm:    { alert: "[!ACCORDION]" }
  - name: no-print
    hide: true
    legacy: { open: "--- no-print ---", close: "--- /no-print ---" }
    rfm:    { alert: "[!NOPRINT]" }
  # … save, new-page/page-break, print-only, challenge, code, quiz, question,
  #    choices, feedback, info, tip, debug …
raw_patterns:                # non-block strings to hide (e.g. asset paths)
  - "hero_image images/"
```

The full marker set is derived from the two attached specs (legacy `kramdown-rpf` and RFM draft).
Entries with only one of `legacy`/`rfm` are fine (e.g. `info`/`tip`/`debug` are RFM-only).

`nttt/markers.py` — loader/accessor (single source of truth):
- `load_markers()` → parsed registry (cached).
- `hideable_strings()` → list of literal marker strings + raw patterns to match against
  Crowdin's `string list` output (both syntaxes).
- `alert_keywords()` / legacy tag helpers for the cleanup modules.

---

## Work items

### 1. Marker registry (new)
- **`nttt/markers.yml`** — the declarative data file above (full set from both specs).
- **`nttt/markers.py`** — loader + accessors described above. Package the `.yml` via
  `setup.py` (`package_data` / `include_package_data`).

### 2. Hide-list generation mode (new) — replaces the grep in `hide-strings.yml`
- **`nttt/hide_strings.py`** — reads `crowdin string list --verbose` output (stdin or file),
  filters rows whose source text contains a hideable marker string (from `markers.hideable_strings()`,
  covering legacy **and** RFM), and prints the numeric string IDs (one per line).
- **CLI wiring** in [arguments.py](nttt/arguments.py) + [__init__.py](nttt/__init__.py):
  add a `--hide-strings` mode flag. When present, `main()` dispatches to `hide_strings` and
  reads stdin instead of running `tidyup_translations`. **Default behaviour (`nttt -Y YES`) is
  unchanged** so the existing download workflow keeps working.

### 3. RFM download-side cleanup (new) — mirrors the legacy section logic
- **`nttt/cleanup_alerts.py`** — `fix_alerts(content, logging)` and
  `revert_alert_translation(name, content, en_content, logging)`:
  - Normalise blockquote alert headers (`>[!TASK]` → `> [!TASK]`, spacing, Crowdin escape quirks).
  - Revert translated alert keywords/`ACCORDION` titles to the English form **by position
    against the English file**, reusing the proven algorithm in
    [`revert_section_translation`](nttt/cleanup_sections.py) (extract → count-match → replace).
  - Keyword set comes from `markers.py`.
- **Wire into [`fix_md_step`](nttt/tidyup.py:55)** alongside the existing legacy steps. Because
  legacy (`--- x ---`) and RFM (`> [!X]`) patterns are disjoint, running both on every file
  safely supports mixed files. Add matching `--disable` flags (`fix_alerts`,
  `revert_alert_translation`) following the existing pattern in [arguments.py](nttt/arguments.py:54).

### 4. Make legacy `cleanup_sections.py` registry-aware (light touch)
- Keep its generic `\w+` regexes, but source the **known legacy tag list and hide flags** from
  `markers.py` so there is one source of truth. Avoid behavioural change to existing tests.

### 5. Example workflows (deliver alongside the tool)
- Add **`doc/workflows/`** with updated copies for content repos to adopt:
  - **`hide-strings.yml`** — install NTTT, then
    `crowdin string list --verbose | nttt --hide-strings > ids.txt` and loop
    `crowdin string edit "$id" --hidden < ids.txt`. (Replaces the grep/awk/sed pipeline and
    fixes the existing bug where the `while read` loop receives no piped input.)
  - `nttt-processing.yml` / `upload-sources.yml` — carried over; note any version bump.
- Reference them from the README.

### 6. Tests (follow existing two-layer pattern)
- **Unit tests** in `unit_test/`: `test_markers.py` (registry load + hideable strings),
  `test_hide_strings.py` (filter sample `crowdin string list` text → expected IDs, legacy + RFM
  + raw pattern rows), `test_cleanup_alerts.py` (normalise + revert, mirroring
  [test_cleanup_sections.py]).
- **Fixture tests** in `test/`: add an RFM/mixed fixture (e.g. `step_7.md` across
  `fixtures/{input,en,output}`) exercising `> [!TASK]`/`> [!HINT]`/`> [!ACCORDION]` reverts plus
  a legacy marker in the same file. Reuse the `_run`/`INSPECT` harness in
  [test_fixtures.py](test/test_fixtures.py).

### 7. Local round-trip fixtures — inspect hide + restore by eye

Beyond pass/fail unit tests, add **inspectable input→output fixtures** (same spirit as the
existing `test/fixtures/{input,en,output}` + `NTTT_INSPECT` harness) so a maintainer can open
the before/after files locally and confirm hiding and restoring look right. Two flows:

**(a) Hide flow — "what would get hidden":**
- `test/fixtures/hide/input/` — sample English source files (legacy, RFM, and mixed) **and** a
  captured `crowdin_string_list.txt` (real `crowdin string list --verbose` output saved once).
- `test/fixtures/hide/output/` (gitignored) — the generated hide-list IDs and a human-readable
  report listing each matched source string next to the marker that matched it, so input vs
  output is reviewable at a glance.
- Test runs `nttt --hide-strings` over the sample and writes both files; assertions check the
  expected IDs/markers are present (legacy + RFM + `hero_image`) and unrelated prose is absent.

**(b) Restore flow — "translated → restored":**
- `test/fixtures/restore/input/` — **translated** step files where markers have been mangled the
  way Crowdin/translators do it (`\---`, jammed lines, translated `--- taak ---`, translated
  `> [!TAREA]`, bad spacing `>[!task]`, mixed legacy+RFM in one file).
- `test/fixtures/restore/en/` — the English reference files (the structural template).
- `test/fixtures/restore/expected/` — the **hand-authored correct restored** version, committed
  so we have a clear oracle.
- `test/fixtures/restore/output/` (gitignored) — what NTTT actually produced.
- Test runs `fix_md_step` and (in normal mode) diffs `output` vs `expected`; in
  `NTTT_INSPECT=1` mode it skips the diff and just writes `output` so you can open
  `input` → `output` → `expected` side by side and eyeball the round-trip.

Document both flows in `doc/transformations.md` so the local-check workflow is discoverable.

### 8. Docs
- Update [doc/transformations.md](doc/transformations.md): add the RFM alert step and the
  hide-list mode to the pipeline description and code map.
- New **`doc/markers.md`**: explains the registry, the legacy↔RFM mapping table, and
  step-by-step "how to add a new block type" for non-Python maintainers.
- Update [README.md](README.md): document `--hide-strings` mode and link the new docs/workflows.
- Bump `nttt/_version.py`.

---

## Verification

1. **Unit + fixture tests:**
   ```bash
   python -m unittest discover -s unit_test -v
   python -m unittest discover -s test -p "test_fixtures.py" -v
   ```
   Inspect mode for the new RFM fixture before locking assertions:
   ```bash
   NTTT_INSPECT=1 python -m unittest discover -s test -p "test_fixtures.py" -v
   ```
2. **Hide-list mode** against a captured sample of `crowdin string list --verbose` output
   (saved as a test fixture): confirm it emits the IDs of legacy markers, RFM alert lines, and
   `hero_image images/` rows — and nothing else.
3. **Mixed-syntax round-trip:** run `fix_md_step` on a file containing both `--- task ---` and
   `> [!TASK]` with a translated copy; confirm both are reverted to English and unrelated prose
   is untouched.
4. **Backward compatibility:** `nttt -Y YES` (default tidyup) still processes legacy-only
   content identically (existing `step_1`–`step_6` fixtures pass unchanged).
5. **Registry editability:** add a dummy block type to `markers.yml`, re-run the hide-list mode,
   confirm it appears with no code change.

---

## Notes / non-goals
- We are **not** stripping markers from files or using placeholder tokens (per the chosen
  "generate hide-list" mechanism). Markers remain in source; Crowdin hides them.
- Renderer HTML output (the two spec docs) is **reference for marker syntax only** — NTTT does
  not render HTML, so those HTML blocks are not test oracles here.
- Workflow ymls live in the content repos; we ship updated **examples**, the team wires them in.

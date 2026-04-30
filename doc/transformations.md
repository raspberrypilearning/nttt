# NTTT: transformations reference

This document describes what **Nina's Translation Tidy-up Tool (NTTT)** changes on disk, so maintainers know what to expect and where to look in code.

## Scope

- **Inputs:** Files under the chosen **input** directory. The tool collects every `meta.yml` and every `*.md` (see `find_files` in [`nttt/utilities.py`](../nttt/utilities.py)).
- **English reference:** A parallel tree (default: `INPUT/../en`) used for `meta.yml` sync and optional section-tag revert.
- **Outputs:** Corresponding paths under the **output** directory (created as needed). After processing, **missing** files/folders can be copied from input and English (`add_missing_entries`).

NTTT does **not** process standalone `.html` files. HTML-related steps run on **HTML inside Markdown**.

---

## High-level pipeline (`fix_md_step`)

For each `.md` file, [`nttt/tidyup.py`](../nttt/tidyup.py) applies, in order:

1. **`fix_sections`** — normalise `---` section lines (Crowdin quirks).
2. **`fix_alerts`** — normalise modern `> [!TYPE]` alert markers.
3. **`revert_section_translation`** — optional; restore English section tag lines when structure matches.
4. **`revert_alert_translation`** — optional; restore English alert type tokens when structure matches.
5. **`trim_md_tags`** — strip padding inside paired Markdown delimiters (outside ` ``` ` fences).
6. **`trim_html_tags`** — strip padding inside simple inline HTML tags (outside single `` ` `` spans).
7. **`fix_codeblocks`** — normalise modern fenced-code info strings.
8. **`trim_formatting_tags`** — normalise `{ … }` attribute blocks after a word (Scratch/Pico-style).
9. **URL rewrite:** replace `/en/` with `/<language>/` everywhere in the file body.

Steps 1–5 can be skipped via **`--disable`** (see [`nttt/arguments.py`](../nttt/arguments.py)).

`meta.yml` is handled separately by **`fix_meta`** (YAML round-trip, revert non-translatable keys from English). This doc focuses on Markdown/HTML-style transforms.

---

## 1. Section markers (`nttt/cleanup_sections.py`)

**Function:** `fix_sections`

| Behaviour | Purpose |
|-----------|---------|
| Replace `\---` with `---` | Crowdin sometimes escapes section markers. |
| Normalise `--` / `---` wrappers around section names | Fix missing dash or inconsistent spacing; target form **`--- <tag> ---`**. Tags allow word chars, digits, hyphens, and certain Unicode space characters inside the name. |
| Normalise closing sections | **`--- /tag ---`** — removes extra spaces between `/` and the tag name. |
| Split jammed section lines | Restore newline between adjacent **`--- … ---`** lines when Crowdin merges them (e.g. hints/hint); regex also tolerates some translator edits. |
| Repair broken collapse/title blocks | Restore **`--- collapse ---`** plus YAML-style **`title:`** block when Crowdin breaks the structure; colons may be ASCII or full-width (`：`). |

**Function:** `revert_section_translation` (requires English `.md`)

- Collects lines matching **`--- <anything> ---`** in translation and English.
- If **counts match**, replaces each translated section line with the **English** line at the same index (keeps English tag names, e.g. `task` vs translated word).
- If counts differ, logs a **warning** to stderr and leaves the file unchanged for this step.

---

## 2. Modern alerts (`nttt/cleanup_alerts.py`)

**Function:** `fix_alerts`

- Normalises modern alert markers such as `> [!TASK]`, `> [!HINT]`, `> [!ACCORDION] Title`, and nested markers such as `> > [!HINT]`.
- Fixes spacing and casing around the marker: `>[ ! task ]` → `> [!TASK]`.
- Preserves any title text after the marker because it is translatable.

**Function:** `revert_alert_translation` (requires English `.md`)

- Collects alert marker lines in translation and English.
- If **counts and nesting depth match**, replaces only the translated alert type token with the English token.
- If structure differs, logs a warning and leaves alert types unchanged for this step.

---

## 3. Markdown delimiters (`nttt/cleanup_markdown.py`)

**Function:** `trim_md_tags`

- Splits content on **` ``` `** (triple backtick). **`apply_to_every_other_part`** runs trimming only on segments **outside** fenced blocks (indices 0, 2, 4, …); fence interiors are untouched.
- Per line outside fences:
  - **List lines:** odd number of `*` and line starts with `*` after `lstrip` → only the substring **after the first `*`** is trimmed (preserves the bullet marker).
  - Otherwise the **whole line** is trimmed.
- **Trim rule:** regex finds paired **`` ` ``**, **`_` … `___`**, or **`*` … `***`** wrapping content; inner content is **`.strip()`**; delimiters unchanged.

Logging can record each replacement (`log_replacement`).

---

## 4. Inline HTML (`nttt/cleanup_html.py`)

**Function:** `trim_html_tags`

- Splits on **single** `` ` ``. Only **even-index** segments are processed; **inline code** segments are preserved.
- Matches **paired** tags: `<tagName>…</tagName>` where `tagName` is **word characters + digits only** (no hyphenated custom elements in the pattern). Inner HTML is **`.strip()`**.
- Does **not** handle attributes on the opening tag, self-closing tags, or arbitrary XML namespaces.

---

## 5. Codeblock info strings (`nttt/cleanup_codeblocks.py`)

**Function:** `fix_codeblocks`

- Normalises opening fenced-code lines such as ```` ```python filename="button.py" ````.
- Lowercases the language token and attribute keys/values.
- Normalises quotes and spacing around `=`.
- Collapses spaces inside `line_highlights`, e.g. `"3, 5-6"` → `"3,5-6"`.
- If the translated language token is not recognised and the English file is available, restores the English language token at the same fence index.
- Does **not** change code inside the block or closing fences.

---

## 6. Formatting braces (`nttt/cleanup_formatting.py`)

**Function:** `trim_formatting_tags`

- Single-pass regex over the **entire** file (no code-fence splitting).
- Targets patterns like **`word { … key = "value" … }`** with flexible Unicode spaces, colons, and quotes (see [`nttt/constants.py`](../nttt/constants.py) `RegexConstants`).
- **Lowercases** the attribute name and value.
- Normalises "blank" link targets: values matching **`_` + spaces + `blank`** → **`_blank`**.

---

## 7. Locale URLs (`nttt/tidyup.py`)

After cleanup: **replace every `/en/` with `/<language>/`** in the Markdown file (`language` from resolved CLI args, defaulting from input folder basename).

---

## Operational notes

- **Confirmation:** Unless **`-Y`**, the tool lists files and waits for **`y`** before writing.
- **Volunteer acknowledgements / missing files:** Separate from Markdown transforms; see `add_volunteer_acknowledgement` and `add_missing_entries` in [`nttt/tidyup.py`](../nttt/tidyup.py).
- **Logging:** Several modules accept a `logging` object for replacement traces (`nttt_logging`).

---

## Strip / restore workflow

`nttt strip` prepares English source for Crowdin by replacing non-translatable markers with deterministic placeholders. `nttt restore` regenerates the same placeholder map from `en/` and re-injects the markers into translated files after Crowdin download.

Typical workflow:

1. Upload side: `nttt strip -i en/ -o .crowdin-staging/en/`
2. Crowdin translates `.crowdin-staging/en/`
3. Download side: `nttt restore -i fr-FR/ -e en/ -o fr-FR/`
4. Existing tidy-up: `nttt -i fr-FR/ -Y YES`

Markdown placeholders use HTML comments such as `<!-- NTTT:7e3a1b-001 -->`. Configure Crowdin to treat `<!-- NTTT:[^ ]+ -->` as non-translatable.

`strip` currently hides:

- legacy section marker lines such as `--- task ---` and `--- /task ---`
- modern alert type tokens such as `[!TASK]`
- modern fenced-code info strings such as `python filename="button.py"`
- inline kramdown class metadata such as `{:class="block3looks"}`
- non-translatable `meta.yml` keys by dropping anything outside `title`, `description`, `steps`, `meta_title`, and `meta_description`

`restore` is safe to run on older Crowdin downloads that do not contain placeholders; it is a no-op for those files. It warns, but does not fail, if placeholders are missing or unknown.

---

## Quick code map

| Concern | Module |
|---------|--------|
| Orchestration | `nttt/tidyup.py`, `nttt/__init__.py` |
| CLI / disable flags | `nttt/arguments.py` |
| Sections | `nttt/cleanup_sections.py` |
| Modern alerts | `nttt/cleanup_alerts.py` |
| Markdown emphasis / code delimiters | `nttt/cleanup_markdown.py` |
| Inline HTML | `nttt/cleanup_html.py` |
| Codeblock info strings | `nttt/cleanup_codeblocks.py` |
| Brace attributes | `nttt/cleanup_formatting.py` |
| Strip / restore | `nttt/strip.py`, `nttt/restore.py` |
| Split "every other segment" | `nttt/utilities.py` → `apply_to_every_other_part` |

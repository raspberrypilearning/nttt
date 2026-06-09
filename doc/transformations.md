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

1. **`restore_tree`** — for non-English locale folders, restore Markdown markers stripped before Crowdin upload.
2. **`fix_sections`** — normalise `---` section lines (Crowdin quirks).
3. **`revert_section_translation`** — optional; restore English section tag lines when structure matches.
4. **`trim_md_tags`** — strip padding inside paired Markdown delimiters (outside ` ``` ` fences).
5. **`trim_html_tags`** — strip padding inside simple inline HTML tags (outside single `` ` `` spans).
6. **`trim_formatting_tags`** — normalise `{ … }` attribute blocks after a word (Scratch/Pico-style).
7. **URL rewrite:** replace `/en/` with `/<language>/` everywhere in the file body.

Steps 1–5 can be skipped via **`--disable`** (see [`nttt/arguments.py`](../nttt/arguments.py)).

`meta.yml` is handled separately by **`fix_meta`** (YAML round-trip, revert non-translatable keys from English). This doc focuses on Markdown/HTML-style transforms.

---

## Crowdin marker strip/restore (`nttt/strip.py`, `nttt/restore.py`)

**Modes:** `--mode strip`, `--mode restore`, and default `--mode tidy`.

| Mode | Behaviour |
|------|-----------|
| `strip` | Runs on `en/` before Crowdin upload. Removes structural-only markers and keeps labelled marker text translatable. |
| `restore` | Runs on a locale folder after Crowdin download. Rebuilds markers from the matching English file. |
| `tidy` | For non-English locale folders, runs restore first, then the existing tidy transforms. |

**Marker classification (`nttt/markers.py`):**

| Kind | Pattern | Strip output | Restore output |
|------|---------|--------------|----------------|
| Modern bare | `> [!TASK]`, `> [!SAVE]`, nested forms like `> > [!HINT]` | Dropped. A following empty blockquote line (`>`, `> >`) is also dropped. | Copied back from `en/`. |
| Modern labelled | `> [!ACCORDION] Where are my voice recordings stored?` | Rewritten to `> Where are my voice recordings stored?`. | Rewritten to `> [!ACCORDION] <translated label>`. |
| Legacy bare | `--- task ---`, `--- /task ---`, `--- print-only ---`, `--- feedback ---` | Dropped. | Copied back from `en/`. |

Restore uses line-index alignment against the stripped English file. If the translated file already contains at least as many legacy bare marker lines as the English reference, restore is skipped for that file to avoid duplicating markers. If the translated file has a different number of lines from the stripped English reference, NTTT logs a warning and leaves that file unchanged for this step.

Fenced code blocks split by ` ``` ` are not stripped.

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

## 2. Markdown delimiters (`nttt/cleanup_markdown.py`)

**Function:** `trim_md_tags`

- Splits content on **` ``` `** (triple backtick). **`apply_to_every_other_part`** runs trimming only on segments **outside** fenced blocks (indices 0, 2, 4, …); fence interiors are untouched.
- Per line outside fences:
  - **List lines:** odd number of `*` and line starts with `*` after `lstrip` → only the substring **after the first `*`** is trimmed (preserves the bullet marker).
  - Otherwise the **whole line** is trimmed.
- **Trim rule:** regex finds paired **`` ` ``**, **`_` … `___`**, or **`*` … `***`** wrapping content; inner content is **`.strip()`**; delimiters unchanged.

Logging can record each replacement (`log_replacement`).

---

## 3. Inline HTML (`nttt/cleanup_html.py`)

**Function:** `trim_html_tags`

- Splits on **single** `` ` ``. Only **even-index** segments are processed; **inline code** segments are preserved.
- Matches **paired** tags: `<tagName>…</tagName>` where `tagName` is **word characters + digits only** (no hyphenated custom elements in the pattern). Inner HTML is **`.strip()`**.
- Does **not** handle attributes on the opening tag, self-closing tags, or arbitrary XML namespaces.

---

## 4. Formatting braces (`nttt/cleanup_formatting.py`)

**Function:** `trim_formatting_tags`

- Single-pass regex over the **entire** file (no code-fence splitting).
- Targets patterns like **`word { … key = "value" … }`** with flexible Unicode spaces, colons, and quotes (see [`nttt/constants.py`](../nttt/constants.py) `RegexConstants`).
- **Lowercases** the attribute name and value.
- Normalises "blank" link targets: values matching **`_` + spaces + `blank`** → **`_blank`**.

---

## 5. Locale URLs (`nttt/tidyup.py`)

After cleanup: **replace every `/en/` with `/<language>/`** in the Markdown file (`language` from resolved CLI args, defaulting from input folder basename).

---

## Operational notes

- **Confirmation:** Unless **`-Y`**, the tool lists files and waits for **`y`** before writing.
- **Volunteer acknowledgements / missing files:** Separate from Markdown transforms; see `add_volunteer_acknowledgement` and `add_missing_entries` in [`nttt/tidyup.py`](../nttt/tidyup.py).
- **Logging:** Several modules accept a `logging` object for replacement traces (`nttt_logging`).

---

## Quick code map

| Concern | Module |
|---------|--------|
| Orchestration | `nttt/tidyup.py`, `nttt/__init__.py` |
| CLI / disable flags | `nttt/arguments.py` |
| Sections | `nttt/cleanup_sections.py` |
| Markdown emphasis / code delimiters | `nttt/cleanup_markdown.py` |
| Inline HTML | `nttt/cleanup_html.py` |
| Brace attributes | `nttt/cleanup_formatting.py` |
| Split "every other segment" | `nttt/utilities.py` → `apply_to_every_other_part` |

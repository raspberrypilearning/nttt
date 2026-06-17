# NTTT: marker registry

NTTT supports two markdown syntaxes for Raspberry Pi project content, which may
appear **in the same file**:

- **legacy** (`kramdown-rpf`): `--- task ---` … `--- /task ---`
- **RFM** (Raspberry Flavoured Markdown / GFM alerts): `> [!TASK]`, `> [!HINT]`, `> [!ACCORDION] Title`

The list of markers lives in one data file — [`nttt/markers.yml`](../nttt/markers.yml) —
so it can be changed **without editing Python**. It is the single source of truth for:

1. **Hiding** — which marker strings NTTT lists for Crowdin to hide from translators
   (`nttt --hide-strings`, see below).
2. **Restoring** — which RFM alert keywords NTTT reverts back to English on download
   (see [`nttt/cleanup_alerts.py`](../nttt/cleanup_alerts.py)).

> The legacy `--- … ---` normalisation in [`nttt/cleanup_sections.py`](../nttt/cleanup_sections.py)
> is intentionally **syntax-generic** (it must cope with arbitrary translated tag
> names), so it does not read the registry. The registry drives hiding and the RFM
> alert handling.

## Editing `markers.yml` (no Python needed)

Each block type is one list entry:

```yaml
  - name: task
    hide: true
    legacy: { open: "--- task ---", close: "--- /task ---" }
    rfm:    { alert: "[!TASK]" }
```

- `hide: true` lists this marker for Crowdin to hide; `false` keeps it visible.
- `legacy.open` / `legacy.close` are the exact marker lines (`close` is optional —
  some blocks, e.g. `save`, have no closing marker).
- `rfm.alert` is the alert token exactly as written, including the brackets.
- Include only the syntaxes a block has (some are RFM-only, e.g. `info`/`tip`/`debug`).

`raw_patterns:` holds non-block strings to hide (matched as plain substrings), e.g.
`hero_image images/`.

**To add a block type:** copy an entry, change the values, run the tests:

```bash
python -m unittest discover -s unit_test
```

## Legacy ↔ RFM mapping

| Block        | Legacy                         | RFM alert                     | Hidden |
|--------------|--------------------------------|-------------------------------|:------:|
| task         | `--- task ---`                 | `[!TASK]`                     | yes |
| hints        | `--- hints ---`                | *(grouped hints)*             | yes |
| hint         | `--- hint ---`                 | `[!HINT]`                     | yes |
| collapse     | `--- collapse ---`             | `[!ACCORDION]` *(+ title)*    | yes |
| challenge    | `--- challenge ---`            | `[!CHALLENGE]`                | yes |
| code         | `--- code ---`                 | *(fenced-code attributes)*    | yes |
| save         | `--- save ---`                 | `[!SAVE]`                     | yes |
| new-page     | `--- new-page ---`             | `<br class="page-break" />`   | yes |
| no-print     | `--- no-print ---`             | `[!NOPRINT]`                  | yes |
| print-only   | `--- print-only ---`           | `[!PRINTONLY]`                | yes |
| quiz         | `--- quiz ---`                 | —                             | yes |
| question     | `--- question ---`             | —                             | yes |
| choices      | `--- choices ---`              | —                             | yes |
| feedback     | `--- feedback ---`             | —                             | yes |
| info         | —                              | `[!INFO]`                     | yes |
| tip          | —                              | `[!TIP]`                      | yes |
| debug        | —                              | `[!DEBUG]`                    | yes |

## Hide-strings mode

NTTT generates the Crowdin hide-list itself (replacing the old grep pipeline). It
reads `crowdin string list --verbose` on stdin and prints the IDs of any string
whose source text contains a hideable marker:

```bash
crowdin string list --verbose | nttt --hide-strings > ids.txt
while read -r id; do crowdin string edit "$id" --hidden; done < ids.txt
```

See [`doc/workflows/hide-strings.yml`](workflows/hide-strings.yml) for the CI version.

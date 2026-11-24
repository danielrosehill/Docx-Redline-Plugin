---
name: rtl-docx
description: Handle Hebrew, Arabic or other right-to-left Word .docx files: read, edit, redline and check direction (RTL, bidi).
---

# Right-to-left .docx

Word stores text in logical order. Direction comes from markup, so text can read correctly in a terminal and still display wrongly.

| Level | Markup | Effect if missing |
|---|---|---|
| Paragraph | `w:bidi` in `w:pPr` (or its style) | Paragraph, numbering and punctuation align left |
| Run | `w:rtl` in `w:rPr` | Punctuation and numbers land on the wrong side; complex-script font and size ignored |
| Font/size | `w:cs` font, `w:szCs`, `w:bCs` | RTL text uses different font, size or weight from what is set |
| Comment | same markup in `comments.xml` | Comment reads left-to-right |

## Steps

1. Read with `${PLUGIN_ROOT}/scripts/docx.py show FILE`. Judge direction from the rendered page, never from terminal output.
2. Edit with the `redline-docx` skill, with `find` text in logical order, copied from `show`. Never reverse text and never insert direction control characters (U+200E, U+200F, U+202A-E) to fix a display problem.
3. `docx.py apply` stops if inserted RTL text lacks `w:rtl`, and marks RTL comments RTL. `docx.py check-rtl FILE` reports it for any file. "existing" lines may be fine: a style can supply direction.
4. Geresh/gershayim (`׳ ״`) and ASCII quotes (`' "`) differ: match the document's own.
5. Render with `docx.py pdf` and look at: alignment, paragraph numbers on the right, final punctuation on the left, dates, phone and reference numbers in order, Latin words inside RTL sentences.

## Notes

- Keep Latin words, URLs and numbers in their own runs when the document does.
- LibreOffice substitutes missing fonts (for example David), so spacing can differ from Word.

---
name: redline-docx
description: Edit a Word .docx with real tracked changes and comments (redline a contract, affidavit or draft), no Word, Hebrew/Arabic safe.
---

# Redline a .docx

1. Read it first (`read-docx`). Agree the substance of each change with the user.
2. Write an edits JSON file (format: `${PLUGIN_ROOT}/scripts/docx.py --help`). Keep each edit to the fewest words. Use a comment for a question, an edit for a wording change.
3. `${PLUGIN_ROOT}/scripts/docx.py apply IN.docx edits.json -o OUT.docx --author "User Name"`. The input is never modified. It stops if a `find` string does not match exactly once, and checks that rejecting every change restores the source text.
4. `docx.py list OUT.docx`, then render with `docx.py pdf` and look at the pages.
5. Give the user a plain list of the changes before the file is sent to anyone.

## Notes

- The author name appears on every change: use the user's name.
- Right-to-left runs keep their direction; comments in RTL scripts are marked RTL.
- Files with personal data stay out of git unless the user says otherwise.

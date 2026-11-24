---
name: finalise-docx
description: Accept or reject all tracked changes in a Word .docx and produce a clean copy, without Microsoft Word.
---

# Accept or reject all changes

1. `${PLUGIN_ROOT}/scripts/docx.py list FILE` and confirm with the user which way to resolve them.
2. `${PLUGIN_ROOT}/scripts/docx.py accept FILE -o CLEAN.docx` (or `reject`). The input is kept.
3. `docx.py list CLEAN.docx` should show no revisions. Comments are not removed.

# Docx Redline

Work with Word `.docx` files from an AI agent on Linux or macOS, without Microsoft Word: real tracked changes, comments, accept/reject, PDF rendering. Right-to-left text (Hebrew, Arabic) keeps its direction.

## Skills

- `read-docx` -- read text, tracked changes and comments; render to PDF
- `redline-docx` -- apply edits as tracked changes and comments, with an automatic check
- `finalise-docx` -- accept or reject everything into a clean copy

`scripts/docx.py` is a standalone CLI (`uv` only; LibreOffice Writer (`libreoffice-writer`) for PDF).

The editing engine is [docx-editor](https://github.com/pablospe/docx-editor) (MIT). This plugin adds the JSON edit list, exactly-once matching, the restore check and RTL comments.

## Installation

```bash
claude plugins install docx-redline@danielrosehill
```

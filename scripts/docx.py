#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["docx-editor==0.9.0"]
# ///
"""Read, redline (real Word tracked changes + comments), verify and render .docx. No Word needed.

  docx.py show FILE [--view visible|original|markup]
  docx.py list FILE                                  revisions and comments
  docx.py apply FILE EDITS.json -o OUT --author NAME
  docx.py verify ORIGINAL OUT                        rejecting all changes must give ORIGINAL's text
  docx.py accept|reject FILE -o OUT                  resolve every tracked change
  docx.py pdf FILE [-o DIR]                          render with LibreOffice

EDITS.json is a list; each find must match exactly once:
  {"op":"replace","find":"...","with":"..."}   {"op":"delete","find":"..."}
  {"op":"insert_after","find":"...","text":"..."}   {"op":"insert_before", ...}
  {"op":"comment","find":"...","text":"..."}
"""
import argparse, json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
from docx_editor import Document

RTL = re.compile(r"[֐-ࣿיִ-﷿ﹰ-﻿]")


def text(path, view):
    with tempfile.TemporaryDirectory() as t:
        c = Path(t) / "c.docx"; shutil.copy(path, c)
        with Document.open(str(c), author="reader") as d:
            return {"visible": d.get_visible_text, "original": d.get_original_text,
                    "markup": d.get_markup_text}[view]()


def rtl_comments(path):
    """docx-editor writes comment text left-to-right; mark RTL-script comments as RTL."""
    tmp = Path(str(path) + ".tmp")
    with zipfile.ZipFile(path) as z, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as o:
        for i in z.infolist():
            b = z.read(i)
            if i.filename == "word/comments.xml":
                def para(m):
                    p = m[0]
                    if not RTL.search(p): return p
                    if "<w:bidi" not in p:
                        p = re.sub(r"<w:pPr>(<w:pStyle[^>]*/>)?", lambda k: k[0] + "<w:bidi/>", p, count=1) if "<w:pPr>" in p \
                            else re.sub(r"(<w:p\b[^>]*>)", r"\1<w:pPr><w:bidi/></w:pPr>", p, count=1)
                    def run(r):
                        r = r[0]
                        if "<w:rtl" in r or not RTL.search(r): return r
                        return r.replace("</w:rPr>", "<w:rtl/></w:rPr>", 1) if "</w:rPr>" in r \
                            else re.sub(r"(<w:r\b[^>]*>)", r"\1<w:rPr><w:rtl/></w:rPr>", r, count=1)
                    return re.sub(r"<w:r\b[^>]*>.*?</w:r>", run, p, flags=re.S)
                b = re.sub(r"<w:p\b[^>]*>.*?</w:p>", para, b.decode(), flags=re.S).encode()
            o.writestr(i, b)
    tmp.replace(path)


def unique(d, s):
    n = d.count_matches(s)
    if n != 1: sys.exit(f"find must match exactly once, matched {n}: {s!r}")
    return d.find_text(s)


def apply(src, edits, out, author):
    out = Path(out)
    if out.resolve() == Path(src).resolve(): sys.exit("refusing to overwrite the input")
    shutil.copy(src, out)
    try:
        with Document.open(str(out), author=author) as d:
            for e in json.loads(Path(edits).read_text()):
                m, op = unique(d, e["find"]), e["op"]
                if op == "replace": d.replace(m, e["with"])
                elif op == "delete": d.delete(m)
                elif op == "insert_after": d.insert_after(m, e["text"])
                elif op == "insert_before": d.insert_before(m, e["text"])
                elif op == "comment": d.add_comment(e["find"], e["text"])
                else: sys.exit(f"unknown op {op}")
            d.save()
        rtl_comments(out)
    except BaseException:
        out.unlink(missing_ok=True); raise
    verify(src, out)


def verify(a, b):
    ok = text(a, "visible") == text(b, "original")
    print("VERIFY", "ok: rejecting all changes restores the source text" if ok else "FAILED")
    if not ok: sys.exit(1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="c", required=True)
    q = s.add_parser("show"); q.add_argument("f"); q.add_argument("--view", default="visible", choices=["visible", "original", "markup"])
    q = s.add_parser("list"); q.add_argument("f")
    q = s.add_parser("apply"); q.add_argument("f"); q.add_argument("edits"); q.add_argument("-o", required=True); q.add_argument("--author", required=True)
    q = s.add_parser("verify"); q.add_argument("f"); q.add_argument("out")
    for c in ("accept", "reject"):
        q = s.add_parser(c); q.add_argument("f"); q.add_argument("-o", required=True)
    q = s.add_parser("pdf"); q.add_argument("f"); q.add_argument("-o", default=".")
    a = p.parse_args()
    if a.c == "show": print(text(a.f, a.view))
    elif a.c == "apply": apply(a.f, a.edits, a.o, a.author)
    elif a.c == "verify": verify(a.f, a.out)
    elif a.c == "pdf":
        with tempfile.TemporaryDirectory() as t:
            subprocess.run(["soffice", f"-env:UserInstallation=file://{t}", "--headless", "--convert-to", "pdf",
                            "--outdir", a.o, a.f], check=True)
        if not (Path(a.o) / (Path(a.f).stem + ".pdf")).exists():  # soffice can fail with exit code 0
            sys.exit("no PDF produced: is libreoffice-writer installed?")
    elif a.c == "list":
        with tempfile.TemporaryDirectory() as t:
            c = Path(t) / "c.docx"; shutil.copy(a.f, c)
            with Document.open(str(c), author="reader") as d:
                for r in d.list_revisions(): print(r)
                for r in d.list_comments(): print(r)
    else:
        if Path(a.o).resolve() == Path(a.f).resolve(): sys.exit("refusing to overwrite the input")
        shutil.copy(a.f, a.o)
        with Document.open(a.o, author="reviewer") as d:
            d.accept_all() if a.c == "accept" else d.reject_all(); d.save()


if __name__ == "__main__":
    main()

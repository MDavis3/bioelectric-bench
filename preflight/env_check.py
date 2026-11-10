#!/usr/bin/env python3
"""Preflight gate: tools needed for extraction and scoring are present.
Connector checks (PubMed, bioRxiv, Elicit, web search) are done by the agent itself:
make one trivial call to each and record the result with harness/state.py log.
"""
import importlib
import shutil
import sys

need_py = ["fitz", "matplotlib"]
nice_py = ["pandas", "sklearn", "pdfplumber"]
need_bin = ["git"]
nice_bin = ["tesseract", "ocrmypdf", "pdftotext"]

bad = False
for m in need_py + nice_py:
    try:
        importlib.import_module(m)
        print(f"ok   py  {m}")
    except ImportError:
        print(f"{'MISS' if m in need_py else 'warn'} py  {m}")
        bad |= m in need_py
for b in need_bin + nice_bin:
    ok = shutil.which(b) is not None
    print(f"{'ok  ' if ok else ('MISS' if b in need_bin else 'warn')} bin {b}")
    bad |= (not ok and b in need_bin)
if not shutil.which("tesseract"):
    print("note: without tesseract, scanned pre-1970 papers can't be OCR'd. Run setup.sh.")
print("ENV FAIL" if bad else "ENV PASS")
sys.exit(1 if bad else 0)

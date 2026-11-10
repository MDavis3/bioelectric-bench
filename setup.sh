#!/usr/bin/env bash
# One-time environment setup. Safe to re-run.
set -u
pip install --quiet --break-system-packages pymupdf pdfplumber pandas scikit-learn matplotlib pillow 2>/dev/null \
  || pip install --quiet pymupdf pdfplumber pandas scikit-learn matplotlib pillow
if command -v apt-get >/dev/null 2>&1; then
  (sudo -n true 2>/dev/null && SUDO=sudo) || SUDO=""
  $SUDO apt-get install -y -qq tesseract-ocr ocrmypdf poppler-utils >/dev/null 2>&1 \
    || echo "warn: could not apt-install OCR tools; scanned papers will need another OCR route"
fi
python3 preflight/env_check.py

#!/usr/bin/env python3
"""Blind images before scoring: copy each photo to a random file name, strip metadata
(EXIF, which can carry time and order), optionally crop to a fixed region, and shuffle.

  python wetlab/prep_images.py RAW_DIR wetlab/batches/batch_01 [--crop x0,y0,x1,y1]
RAW_DIR files must be named <dishcode>_<worm>.<ext> (one animal per image).
Writes <stem>_blind/ with random names and <stem>_image_key.csv (random name -> code, worm).
Seal the image key before scoring. The image scorer sees only <stem>_blind/.
"""
import argparse
import csv
import random
import secrets
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("stem")
    ap.add_argument("--crop", default=None)
    a = ap.parse_args()
    try:
        from PIL import Image
    except ImportError:
        sys.exit("pip install pillow")
    out = Path(f"{a.stem}_blind")
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in Path(a.raw).iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".tif", ".tiff"))
    random.Random(secrets.randbits(64)).shuffle(files)
    rows = []
    for f in files:
        code, _, worm = f.stem.partition("_")
        name = secrets.token_hex(6) + ".png"
        im = Image.open(f).convert("RGB")
        if a.crop:
            im = im.crop(tuple(int(v) for v in a.crop.split(",")))
        clean = Image.new("RGB", im.size)
        clean.paste(im)
        clean.save(out / name)
        rows.append([name, code, worm])
    with open(f"{a.stem}_image_key.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["image", "code", "worm"])
        w.writerows(rows)
    print(f"{len(rows)} images blinded into {out}. Seal {a.stem}_image_key.csv before scoring.")


if __name__ == "__main__":
    main()

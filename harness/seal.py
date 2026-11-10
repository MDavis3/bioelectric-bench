#!/usr/bin/env python3
"""Seal a file: hash it, copy it into sealed/, record it, and (with --git) commit and push
so a third party (GitHub) holds the timestamp. A name can only be sealed once.

  python harness/seal.py predictions/predictions.jsonl --name test_predictions --git
  python harness/seal.py --verify test_predictions predictions/predictions.jsonl
"""
import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, sha256_file  # noqa: E402

REG = ROOT / "sealed" / "SEALS.json"


def registry():
    return json.loads(REG.read_text()) if REG.exists() else {}


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--name")
    ap.add_argument("--git", action="store_true", help="commit and push the seal")
    ap.add_argument("--verify", metavar="NAME")
    a = ap.parse_args()
    reg = registry()

    if a.verify:
        if a.verify not in reg:
            sys.exit(f"no seal named {a.verify}")
        h = sha256_file(a.file)
        ok = h == reg[a.verify]["sha256"]
        print(("MATCH" if ok else "MISMATCH"), a.verify, h)
        sys.exit(0 if ok else 1)

    if not a.file or not a.name:
        sys.exit("need FILE and --name")
    if a.name in reg:
        sys.exit(f"{a.name} is already sealed at {reg[a.name]['utc']}. Seals are write-once.")
    src = Path(a.file)
    h = sha256_file(src)
    dest = ROOT / "sealed" / f"{a.name}__{h[:12]}{src.suffix}"
    shutil.copy2(src, dest)
    reg[a.name] = {
        "sha256": h,
        "utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": str(src.resolve().relative_to(ROOT)) if src.resolve().is_relative_to(ROOT) else str(src),
        "copy": str(dest.relative_to(ROOT)),
    }
    REG.write_text(json.dumps(reg, indent=2, sort_keys=True))
    print(f"sealed {a.name} sha256={h}")

    if a.git:
        if git("rev-parse", "--is-inside-work-tree").returncode != 0:
            print("WARNING: not a git repo; seal is local only. Set up the public repo (README) and re-push.")
            return
        git("add", str(REG), str(dest))
        c = git("commit", "-m", f"seal {a.name} sha256={h}")
        print(c.stdout.strip() or c.stderr.strip())
        p = git("push")
        if p.returncode != 0:
            print("WARNING: push failed; seal is not externally timestamped yet:\n" + p.stderr.strip())
        else:
            head = git("rev-parse", "HEAD").stdout.strip()
            reg = registry()
            reg[a.name]["remote_commit"] = head
            REG.write_text(json.dumps(reg, indent=2, sort_keys=True))
            git("add", str(REG))
            git("commit", "-m", f"record remote commit for seal {a.name}")
            git("push")
            print(f"pushed: external timestamp recorded at commit {head}")


if __name__ == "__main__":
    main()

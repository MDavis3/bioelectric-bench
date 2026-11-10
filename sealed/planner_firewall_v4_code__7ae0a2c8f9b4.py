#!/usr/bin/env python3
"""Planner firewall v4 = sealed v1 checker + every sealed allow-list config/firewall_allow_v{N}.json (N >= 2) that is
registered in sealed/SEALS.json as firewall_allow_v{N}. Each must match its seal; an unsealed allow-list is ignored
with a warning. Same interface as v1. Later allow-lists need only a new sealed JSON, not new code."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planner_firewall as FW  # noqa: E402
from common import ROOT, sha256_file  # noqa: E402

if __name__ == "__main__":
    reg = json.loads((ROOT / "sealed" / "SEALS.json").read_text())
    for cfg in sorted((ROOT / "config").glob("firewall_allow_v*.json")):
        name = cfg.stem
        if not re.fullmatch(r"firewall_allow_v\d+", name):
            continue
        if name not in reg:
            print(f"WARNING: {cfg.name} is not sealed; ignored", file=sys.stderr)
            continue
        if reg[name]["sha256"] != sha256_file(cfg):
            sys.exit(f"{cfg.name} does not match its seal; refusing")
        c = json.loads(cfg.read_text())
        FW.TEXT_ALLOW |= set(c["text_allow_add"])
        FW.DENIED.extend(g for g in c["denied_add"] if g not in FW.DENIED)
    sys.exit(FW.main())

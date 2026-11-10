#!/usr/bin/env python3
"""Planner firewall v2: the sealed v1 checker (harness/planner_firewall.py) unchanged, plus a sealed allow-list and
extra denied paths from config/firewall_allow_v2.json (seal name firewall_allow_v2).

  python harness/planner_firewall_v2.py check|reply|split|paths   # same interface as v1
Refuses to run if config/firewall_allow_v2.json does not match its seal.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planner_firewall as FW  # noqa: E402
from common import ROOT, sha256_file  # noqa: E402

CFG = ROOT / "config" / "firewall_allow_v2.json"


def load():
    reg = json.loads((ROOT / "sealed" / "SEALS.json").read_text())
    if "firewall_allow_v2" in reg and reg["firewall_allow_v2"]["sha256"] != sha256_file(CFG):
        sys.exit("config/firewall_allow_v2.json does not match its seal (firewall_allow_v2); refusing")
    if "firewall_allow_v2" not in reg:
        print("WARNING: firewall_allow_v2 not sealed yet", file=sys.stderr)
    c = json.loads(CFG.read_text())
    FW.TEXT_ALLOW |= set(c["text_allow_add"])
    FW.DENIED.extend(g for g in c["denied_add"] if g not in FW.DENIED)


if __name__ == "__main__":
    load()
    sys.exit(FW.main())

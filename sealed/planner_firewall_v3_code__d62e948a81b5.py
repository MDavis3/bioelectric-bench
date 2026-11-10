#!/usr/bin/env python3
"""Planner firewall v3 = sealed v1 checker + sealed v2 allow-list + sealed v3 allow-list (config/firewall_allow_v3.json,
seal firewall_allow_v3). Same interface as v1."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import planner_firewall as FW  # noqa: E402
import planner_firewall_v2 as V2  # noqa: E402
from common import ROOT, sha256_file  # noqa: E402

CFG = ROOT / "config" / "firewall_allow_v3.json"

if __name__ == "__main__":
    V2.load()
    reg = json.loads((ROOT / "sealed" / "SEALS.json").read_text())
    if "firewall_allow_v3" in reg and reg["firewall_allow_v3"]["sha256"] != sha256_file(CFG):
        sys.exit("config/firewall_allow_v3.json does not match its seal; refusing")
    c = json.loads(CFG.read_text())
    FW.TEXT_ALLOW |= set(c["text_allow_add"])
    FW.DENIED.extend(g for g in c["denied_add"] if g not in FW.DENIED)
    sys.exit(FW.main())

#!/usr/bin/env python3
"""Write config/harness_manifest_v2.json (sealed as harness_manifest_v2): sha256 of every file that determines a
holdout verdict or an extracted row under harness v2. holdout2.py refuses a counted run if the manifest lacks any
REQUIRED file or any listed file changed. The v1 builder (make_harness_manifest.py) and v1 manifest are untouched.
  python harness/make_harness_manifest_v2.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, sha256_file  # noqa: E402

REQUIRED = ["harness/holdout2.py", "harness/common.py", "harness/score.py", "harness/temporal_holdout.py",
            "harness/derive_features.py", "harness/validate_rows.py", "harness/planner_firewall.py",
            "harness/firewall_check.py", "harness/bound_count.py", "harness/combine_verdicts.py",
            "harness/make_harness_manifest_v2.py", "harness/blind_passes.py", "harness/collect_adjudicated.py",
            "schema/extraction_schema.json", "schema/outcome_categories.json", "extraction/INSTRUCTIONS_v2.md",
            "extraction/ADJUDICATION_v2.md", "config/paper_crosswalk.json"]

if __name__ == "__main__":
    out = {"note": "harness v2: sha256 of files that determine holdout verdicts and extracted rows; sealed as harness_manifest_v2",
           "files": {f: sha256_file(ROOT / f) for f in REQUIRED}}
    (ROOT / "config/harness_manifest_v2.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))

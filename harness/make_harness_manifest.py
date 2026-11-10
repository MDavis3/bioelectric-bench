#!/usr/bin/env python3
"""Write config/harness_manifest.json: sha256 of every file that determines a holdout verdict.
Sealed as harness_manifest; holdout2.py refuses a counted run if any listed file changes.
  python harness/make_harness_manifest.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, sha256_file  # noqa: E402

FILES = ["harness/holdout2.py", "harness/derive_features.py", "harness/common.py", "harness/score.py",
         "harness/temporal_holdout.py", "config/active_schema.json", "schema/outcome_categories.json",
         "schema/extraction_schema.json", "extraction/INSTRUCTIONS.md", "harness/validate_rows.py"]
out = {"note": "sha256 of files that determine holdout verdicts; sealed as harness_manifest",
       "files": {f: sha256_file(ROOT / f) for f in FILES}}
(ROOT / "config/harness_manifest.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))

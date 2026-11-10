#!/usr/bin/env python3
"""Setup-only feasibility counts per family (no outcomes). Input: derived setup rows.
  python harness/setup_counts.py data/setups/setup_pass_derived/all_v2lookup.jsonl [--md out.md]"""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_jsonl, get, norm_val  # noqa: E402

def ctrl(r):
    return norm_val(get(r, "intervention.type")) == "control" or norm_val(r.get("arm_role")) in ("control", "vehicle")

rows = load_jsonl(sys.argv[1])
fams = defaultdict(list)
for r in rows:
    fams[r.get("task_family")].append(r)
out = ["| family | arms | treated | papers | lineages | decades | agents | targets | directional targets | treated rows with direction | applied-field treated |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for f, rs in sorted(fams.items(), key=lambda x: -len(x[1])):
    t = [r for r in rs if not ctrl(r)]
    dirt = {c for r in t if get(r, "drug.vmem_direction_pred") for c in (r.get("_target_components") or [])}
    out.append(f"| {f} | {len(rs)} | {len(t)} | {len({get(r,'source.paper_id') for r in t})} | {len({r.get('_lineage') for r in t})} | "
               f"{len({(get(r,'source.year') or 0)//10*10 for r in t})} | {len({c for r in t for c in r.get('_components') or []})} | "
               f"{len({c for r in t for c in r.get('_target_components') or []})} | {len(dirt)} | "
               f"{sum(1 for r in t if get(r,'drug.vmem_direction_pred'))} | {sum(1 for r in t if get(r,'intervention.type')=='applied_field')} |")
print("\n".join(out))

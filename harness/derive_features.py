#!/usr/bin/env python3
"""Add script-derived setup features to adjudicated rows. Nothing here reads outcomes.

Inputs (all sealed at lock_schema):
  kb/vmem_lookup.json     agents (with aliases) -> canonical agent, target, target_class, action;
                          class_rules: (target_class, action) -> predicted Vmem direction
  config/lab_lineage.json lab surname -> lineage
Adds (top-level fields; extractors never write these):
  _agent_id, _components            canonical agent id(s); combinations split on + ; and / with
  _target_id, _target_components    canonical target(s) from the lookup (extractor's target only as fallback)
  _target_class                     lookup class, or control / combination
  intervention.action               from the lookup when the extractor left it empty
  drug.vmem_direction_pred          depolarize | hyperpolarize | null  (null = unknown, contested,
                                    combination, control, applied field, or agent not in the lookup)
  _dose_bucket, _timing_bucket, _duration_bucket, _fragment, _delivery, _field_dir, _lineage

  python harness/derive_features.py data/raw_extractions/adjudicated.jsonl data/derived/all.jsonl
Prints coverage counts only (no outcome information).
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, get, load_jsonl, norm_val, write_jsonl  # noqa: E402

UNIT_TO_UM = {"m": 1e6, "mm": 1e3, "um": 1.0, "µm": 1.0, "μm": 1.0, "nm": 1e-3, "pm": 1e-6}


def canon(s):
    return re.sub(r"[^a-z0-9+]+", " ", str(s).lower().replace("μ", "u").replace("µ", "u")).strip()


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def dose_bucket(dose, units):
    d = num(dose)
    if d is None or d <= 0:
        return None
    u = (units or "").strip().lower().replace(" ", "")
    if u in UNIT_TO_UM:
        return f"1e{math.floor(math.log10(d * UNIT_TO_UM[u]))}uM"
    return f"{u or 'unitless'}:1e{math.floor(math.log10(d))}"


def timing_bucket(h):
    h = num(h)
    if h is None:
        return None
    return "pre" if h < 0 else "0-3h" if h < 3 else "3-24h" if h < 24 else "24h+"


def duration_bucket(h):
    h = num(h)
    if h is None:
        return None
    return "<3h" if h < 3 else "3-24h" if h < 24 else "1-3d" if h <= 72 else ">3d"


def fragment(stage):
    s = (stage or "").lower()
    for k, v in [("trunk", "trunk"), ("pharyn", "trunk"), ("middle", "trunk"), ("head", "head"), ("tail", "tail"),
                 ("whole", "whole"), ("intact", "whole")]:
        if k in s:
            return v
    return None


def delivery(x):
    s = (x or "").lower()
    for k, v in [("inject", "injection"), ("electro", "electrode"), ("feed", "feeding"), ("bath", "bath"),
                 ("soak", "bath"), ("medium", "bath"), ("light", "light")]:
        if k in s:
            return v
    return "other" if s else None


def field_dir(x):
    s = (x or "").lower()
    if not s:
        return None
    m = re.search(r"(?:anterior|head)[^.;]*?(cathode|anode)", s)
    if m:
        return "anterior_to_" + m.group(1)
    m = re.search(r"posterior[^.;]*?(cathode|anode)", s)
    if m:
        return "anterior_to_" + ("anode" if m.group(1) == "cathode" else "cathode")
    return "other"


def main():
    src, dst = sys.argv[1], sys.argv[2]
    lk = json.loads((ROOT / "kb/vmem_lookup.json").read_text())
    lin = {canon(k): v for k, v in json.loads((ROOT / "config/lab_lineage.json").read_text())["lab_to_lineage"].items()}
    alias = {}
    for name, a in lk["agents"].items():
        for n in [name] + a.get("aliases", []):
            alias[canon(n)] = (name, a)
    rules = {(r["target_class"], r["action"]): r["vmem"] for r in lk["class_rules"]}
    rows = load_jsonl(src)
    cov = Counter()
    for r in rows:
        iv = r.setdefault("intervention", {})
        typ = norm_val(iv.get("type"))
        ctrl = typ == "control" or norm_val(r.get("arm_role")) in ("control", "vehicle")
        raw = str(iv.get("agent") or "")
        whole = alias.get(canon(raw))
        parts = [raw] if whole else [x for x in re.split(r"\s*(?:\+|;|\band\b|\bwith\b)\s*", raw.lower()) if x.strip()]
        hits = [whole] if whole else [alias.get(canon(x)) for x in parts]
        comps, tcomps = [], []
        for x, h in zip(parts, hits):
            if h:
                comps.append(h[0])
                if h[1].get("target_class") not in (None, "control"):
                    tcomps.append(h[1].get("target") or h[0])
            else:
                comps.append(canon(x))
                cov[f"not_in_lookup:{canon(x)}"] += 1
        vm = None
        r["_target_class"] = "control" if ctrl else None
        if not ctrl and len(hits) == 1 and hits[0]:
            name, a = hits[0]
            iv["action"] = iv.get("action") or a.get("action")
            r["_target_class"] = a.get("target_class")
            vm = a["vmem"] if "vmem" in a else rules.get((a.get("target_class"), norm_val(iv.get("action"))))
        elif not ctrl and len(comps) > 1:
            r["_target_class"] = "combination"
        if not ctrl and not tcomps and len(comps) == 1 and iv.get("target"):
            tcomps = [canon(iv["target"])]  # fallback: extractor's target for agents not in the lookup
        r["_agent_id"] = " + ".join(sorted(set(comps))) if comps else None
        r["_components"] = sorted(set(comps))
        r["_target_components"] = sorted(set(tcomps))
        r["_target_id"] = " + ".join(r["_target_components"]) or None
        if vm not in ("depolarize", "hyperpolarize"):
            vm = None  # single null vocabulary: unknown, contested, combination, control, field, not in lookup
        r.setdefault("drug", {})["vmem_direction_pred"] = vm
        r["_dose_bucket"] = dose_bucket(iv.get("dose"), iv.get("dose_units"))
        r["_timing_bucket"] = timing_bucket(iv.get("timing_start_h"))
        r["_duration_bucket"] = duration_bucket(iv.get("duration_h"))
        r["_fragment"] = fragment(r.get("stage"))
        r["_delivery"] = delivery(iv.get("delivery"))
        r["_field_dir"] = field_dir(iv.get("field_direction"))
        lab = canon(get(r, "source.lab") or "")
        r["_lineage"] = lin.get(lab, lab or None)
        if not ctrl:
            cov[f"vmem:{vm}"] += 1
            for k in ("_dose_bucket", "_timing_bucket", "_duration_bucket", "_fragment", "_target_id"):
                cov[f"{k}:{'set' if r[k] else 'null'}"] += 1
        if lab not in lin:
            cov[f"lab_not_in_lineage_map:{lab}"] += 1
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(dst, rows)
    print(f"rows: {len(rows)} -> {dst}")
    for k, v in sorted(cov.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

"""Shared helpers for the bioelectric prediction benchmark harness."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPS = 1e-6


def load_jsonl(path):
    path = Path(path)
    rows = []
    if path.is_dir():
        for p in sorted(path.glob("*.jsonl")):
            rows.extend(load_jsonl(p))
        return rows
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{i}: bad JSON ({e})")
    return rows


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def active_schema():
    p = ROOT / "config" / "active_schema.json"
    if p.exists():
        return json.loads(p.read_text())
    return {"version": 1, "extraction": "schema/extraction_schema.json", "categories": "schema/outcome_categories.json"}


def load_categories():
    with open(ROOT / active_schema()["categories"]) as f:
        return {k: v["categories"] for k, v in json.load(f)["task_families"].items()}


def load_schema():
    with open(ROOT / active_schema()["extraction"]) as f:
        return json.load(f)


def outcome_dist(row, cats):
    """Normalized outcome distribution over the family's categories."""
    fam = row["task_family"]
    if fam not in cats:
        raise ValueError(f"{row.get('item_id')}: unknown task_family {fam}")
    counts = {c: 0.0 for c in cats[fam]}
    for o in row.get("outcomes", []):
        if o["category"] not in counts:
            raise ValueError(f"{row.get('item_id')}: category {o['category']} not in {fam}")
        counts[o["category"]] += float(o["count"])
    total = sum(counts.values())
    if total <= 0:
        raise ValueError(f"{row.get('item_id')}: no outcome counts")
    return {c: v / total for c, v in counts.items()}


def normalize(probs, categories, smooth=0.0):
    p = {c: max(float(probs.get(c, 0.0)), 0.0) for c in categories}
    s = sum(p.values())
    k = len(categories)
    if s <= 0:
        return {c: 1.0 / k for c in categories}
    p = {c: v / s for c, v in p.items()}
    if smooth:
        p = {c: (1 - smooth) * v + smooth / k for c, v in p.items()}
    return p


def get(row, dotted, default=None):
    cur = row
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


NN_FEATURES = {
    # feature: weight
    "organism": 1.0,
    "species": 0.5,
    "stage": 1.0,
    "injury": 0.5,
    "intervention.type": 3.0,
    "intervention.target": 3.0,
    "intervention.agent": 2.0,
    "intervention.timing": 1.0,
    "intervention.delivery": 0.5,
    "intervention.field_direction": 2.0,
}


def norm_val(v):
    if v is None:
        return None
    return str(v).strip().lower()


def similarity(a, b):
    s = 0.0
    for f, w in NN_FEATURES.items():
        va, vb = norm_val(get(a, f)), norm_val(get(b, f))
        if va is not None and va == vb:
            s += w
    return s

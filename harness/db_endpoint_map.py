#!/usr/bin/env python3
"""Generate the endpoint term sets from config/db_endpoint_roots_v1.json by ontology closure.
Writes config/db_endpoint_map_v1.json (term IDs only; no gene or phenotype data).

  python harness/db_endpoint_map.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
O = ROOT / "data/db_setup/ontologies"


def parse(path, rels=("is_a",)):
    children, names, cur = defaultdict(set), {}, None
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith("["):
            cur = {} if line == "[Term]" else None
            continue
        if cur is None:
            continue
        if line.startswith("id: "):
            cur["id"] = line[4:]
        elif line.startswith("name: ") and "id" in cur:
            names[cur["id"]] = line[6:]
        elif line.startswith("is_a: ") and "is_a" in rels and "id" in cur:
            children[line[6:].split(" ")[0]].add(cur["id"])
        elif line.startswith("relationship: part_of ") and "part_of" in rels and "id" in cur:
            children[line.split(" ")[2]].add(cur["id"])
    return children, names


def closure(roots, children):
    out, stack = set(), list(roots)
    while stack:
        t = stack.pop()
        if t in out:
            continue
        out.add(t)
        stack.extend(children.get(t, ()))
    return out


def main():
    R = json.loads((ROOT / "config/db_endpoint_roots_v1.json").read_text())
    m = R["mouse"]
    ch, nm = parse(O / "mp.obo")
    inc = closure(m["Y_include_roots"], ch)
    exc = closure(m["Y_exclude_roots"], ch) - closure(m["Y_exclude_exceptions_keep"], ch)
    y = {t for t in inc - exc if not any(w in nm.get(t, "").lower() for w in m["Y_exclude_label_words"])}
    yexc = closure(m["Y_exc_roots"], ch) - closure(m["Y_exc_minus"], ch)
    leth = {t for t in closure(m["lethality_roots"], ch) if any(w in nm.get(t, "") for w in m["lethality_label_words"])}
    z = R["zebrafish"]
    zch, _ = parse(O / "zfa.obo", ("is_a", "part_of"))
    pch, _ = parse(O / "pato.obo")
    gch, _ = parse(O / "go-basic.obo")
    out = {"mouse": {"Y_terms": sorted(y), "Y_exc_terms": sorted(yexc), "lethality_terms": sorted(leth)},
           "zebrafish": {"entity_terms": sorted(closure(z["entity_roots"], zch)),
                         "quality_terms": sorted(closure(z["quality_roots"], pch) - closure(z["quality_exclude_roots"], pch)),
                         "process_terms": sorted(closure(z["process_roots_any_quality"], gch)),
                         "laterality_quality_terms": sorted(closure(z["laterality_quality_roots_any_entity"], pch)),
                         "Y_exc_entity_terms": sorted(closure(z["Y_exc_entity_roots"], zch)),
                         "Y_exc_process_terms": sorted(closure(z["Y_exc_process_roots"], gch))}}
    (ROOT / "config/db_endpoint_map_v1.json").write_text(json.dumps(out, indent=0))
    for sp, d in out.items():
        print(sp, {k: len(v) for k, v in d.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())

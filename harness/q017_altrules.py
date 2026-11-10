#!/usr/bin/env python3
"""Q017 counts-only follow-up: unit counts, ALT blocks and label validation under alternative label rules R2, R3.
Reads ClinVar + hpoa (aspect P only for the >=1-term unit filter and alias resolution); writes integers only.
R2: ALT = dominant AND >=3 missense AND missense share >= 0.80; LOF = >=2 truncating AND truncating share >= 0.50.
R3: ALT = dominant AND >=2 missense AND missense share >= 0.67; LOF as R2. Share = n / (missense + truncating).
Output: data/db_restricted/reply_q017_altrules.json (does not touch the q017_build outputs)."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import q017_build as Q  # noqa: E402
from db_secondary import parse_obo  # noqa: E402

RULES = {"R2": (3, 0.80), "R3": (2, 0.67)}


def lab_fn(nm, nt, dom, min_mis, share):
    tot = nm + nt
    if nt >= 2 and nt / tot >= 0.50:
        return "LOF"
    if dom and nm >= min_mis and nm / tot >= share:
        return "ALT"
    return "GREY"


def main():
    ch, nmz, alt, repl, obs = parse_obo(Q.OBO)
    P, I, dname = Q.load_hpoa(alt, repl, obs)
    plp, mis, trunc, sym, cvn, _ = Q.load_clinvar()
    classes = json.loads((ROOT / "config/db_classes_v1.json").read_text())["genes"]
    import csv
    sym2h = {}
    with open(ROOT / "data/db_setup/hgnc/hgnc_complete_set.txt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            sym2h[r["symbol"]] = r["hgnc_id"]
    for h, s in sym.items():
        sym2h.setdefault(s, h)
    fam = {}
    for r in csv.DictReader(open(ROOT / "data/db_setup/hgnc/gene_has_family.csv")):
        fam.setdefault("HGNC:" + r["hgnc_id"], set()).add(r["family_id"])
    fsize = Counter(f for fs in fam.values() for f in fs)
    block = lambda h: ("F" + min(fam[h], key=lambda f: (fsize[f], int(f)))) if h in fam else "A" + h
    val = json.loads((ROOT / "config/q017_validation_v1.json").read_text())
    pairs = [k for k in plp if k[1] in P]
    out = {}
    for rn, (mm, sh) in RULES.items():
        lab = {}
        for k in pairs:
            nm, nt = len(mis.get(k, ())), len(trunc.get(k, ()))
            if nm + nt == 0:
                lab[k] = "GREY"
                continue
            lab[k] = lab_fn(nm, nt, bool(I.get(k[1], set()) & Q.DOM), mm, sh)
        r = Counter()
        for k, l in lab.items():
            r[f"{classes.get(k[0], {}).get('cls', 'other')}_{l}"] += 1
        res = {f"{c}_{l}": r.get(f"{c}_{l}", 0) for c in ("class", "control", "grey", "other")
               for l in ("ALT", "LOF", "GREY")}
        for c in ("class", "control"):
            res[f"{c}_blocks_ALT"] = len({block(k[0]) for k, l in lab.items()
                                          if l == "ALT" and classes.get(k[0], {}).get("cls") == c})
        v = {"ALT": [0, 0], "LOF": [0, 0]}
        unres = 0
        for side, key in (("ALT", "expected_ALT"), ("LOF", "expected_LOF")):
            for gene, cname, mim in val[key]:
                h, ms = Q.resolve_entry(gene, cname, mim, sym2h, set(plp), P, dname, cvn)
                if not ms:
                    unres += 1
                    continue
                m = mim if mim in ms else sorted(ms, key=int)[0]
                l = lab[(h, m)]
                if l != "GREY":
                    v[side][1] += 1
                    v[side][0] += int(l == side)
        res.update(val_ALT_ok=v["ALT"][0], val_ALT_nongrey=v["ALT"][1], val_LOF_ok=v["LOF"][0],
                   val_LOF_nongrey=v["LOF"][1], val_unresolved=unres)
        out[rn] = res
    p = ROOT / "data/db_restricted/reply_q017_altrules.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build config/db_classes_v1.json (class / grey / control, human anchor) from HGNC gene groups and IUPHAR/GtoPdb.
Preregistration plans/pivot_db_v1.md section C. Reads only predictor-side files in data/db_setup/.

  python harness/db_classes.py
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data" / "db_setup"

CLASS_FAMS = {"177": None, "314": "gap_junction", "288": "gap_junction", "1208": "p_type_pump",
              "1211": "p_type_pump", "415": "v_atpase"}
SUBCLASS_FAMS = [("314", "gap_junction"), ("288", "gap_junction"), ("178", "voltage_gated"), ("161", "ligand_gated")]
GREY_SYMBOL = re.compile(r"^(RYR\d|ITPR\d|TPCN\d|VDAC\d|CLIC\d|MCU.*|MICU\d|ATP2A\d|ATP2C\d|ATP5.*|MT-ATP.*|"
                         r"CLCN[3-7]|MCOLN\d|SMDT1|ANO([3-9]|10)|TMEM175|TMEM38[AB]|ATP7[AB]|ATP13A\d|AQP\d+|PKD2L?\d?_ER)$")
GREY_FAMS = {"2157": "SLC4", "2161": "SLC8", "2162": "SLC9", "2152": "SLC12", "2175": "SLC24", "2177": "SLC26",
             "305": "AQP", "306": "VDAC", "247": "TPCN", "287": "RYR", "297": "ITPR", "644": "ATP5", "1212": "ATP7",
             "1213": "ATP13"}
CONTROL_FAMS = {"752": "SLC", "417": "ABC", "139": "GPCR", "768": "TSPAN", "488": "CLDN", "1239": "TM9SF",
                "1210": "P4_ATPase", "2217": "DISP", "978": "CMTM"}
CONTROL_EXCLUDE_FAMS = {"141", "289", "291", "1161", "1162"}   # olfactory, taste, vomeronasal
CONTROL_EXTRA_SYMBOLS = {"PTCH1", "PTCH2"}
IUPHAR_CLASS_TYPES = {"vgic": "voltage_gated", "lgic": "ligand_gated", "other_ic": "other_channel"}


def load():
    closure = defaultdict(set)
    for r in csv.DictReader(open(D / "hgnc/hierarchy_closure.csv")):
        closure[r["parent_fam_id"]].add(r["child_fam_id"])
    fam_genes = defaultdict(set)
    for r in csv.DictReader(open(D / "hgnc/gene_has_family.csv")):
        fam_genes[r["family_id"]].add("HGNC:" + r["hgnc_id"])
    genes = {}
    with open(D / "hgnc/hgnc_complete_set.txt") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r.get("status", "Approved") != "Approved" or r.get("locus_group") != "protein-coding gene":
                continue
            genes[r["hgnc_id"]] = r["symbol"]
    return closure, fam_genes, genes


def members(fid, closure, fam_genes):
    out = set()
    for c in closure.get(fid, {fid}) | {fid}:
        out |= fam_genes.get(c, set())
    return out


def main():
    closure, fam_genes, genes = load()
    sym2id = {s: i for i, s in genes.items()}
    cls, sub, src = {}, {}, defaultdict(list)
    for fid, s in CLASS_FAMS.items():
        for g in members(fid, closure, fam_genes):
            cls[g] = "class"
            src[g].append("HGNC:" + fid)
    # ATP2B (plasma membrane Ca-ATPases) only, from ATPases Ca2+ transporting
    for g in members("1209", closure, fam_genes):
        if genes.get(g, "").startswith("ATP2B"):
            cls[g] = "class"
            sub[g] = "p_type_pump"
            src[g].append("HGNC:1209/ATP2B")
    # IUPHAR ion channels
    with open(D / "iuphar/targets_and_families.csv") as f:
        next(f)
        for r in csv.DictReader(f):
            t = r["Type"]
            hid = r["HGNC id"].strip()
            if t in IUPHAR_CLASS_TYPES and hid:
                g = hid if hid.startswith("HGNC:") else "HGNC:" + hid
                if g in genes:
                    cls[g] = "class"
                    src[g].append("IUPHAR:" + t)
                    sub.setdefault(g, IUPHAR_CLASS_TYPES[t])
    for fid, name in SUBCLASS_FAMS:
        for g in members(fid, closure, fam_genes):
            if g in cls:
                sub[g] = name
    for fid, name in CLASS_FAMS.items():
        if name:
            for g in members(fid, closure, fam_genes):
                sub[g] = name
    for g in cls:
        sub.setdefault(g, "other_channel")
    # grey zone overrides class
    grey = {}
    for fid, name in GREY_FAMS.items():
        for g in members(fid, closure, fam_genes):
            grey[g] = name
    for g, s in genes.items():
        if GREY_SYMBOL.match(s):
            grey[g] = "symbol_rule"
    for g in list(cls):
        if g in grey:
            del cls[g]
            sub.pop(g, None)
    # control
    ctrl = {}
    excl = set()
    for fid in CONTROL_EXCLUDE_FAMS:
        excl |= members(fid, closure, fam_genes)
    for fid, name in CONTROL_FAMS.items():
        for g in members(fid, closure, fam_genes):
            if g not in cls and g not in grey and g not in excl:
                ctrl[g] = name
    for s in CONTROL_EXTRA_SYMBOLS:
        g = sym2id.get(s)
        if g and g not in cls and g not in grey:
            ctrl[g] = "PTCH"
    out = {"note": "Human-anchor gene classes for plans/pivot_db_v1.md section C. Built by harness/db_classes.py from "
                   "HGNC (data/db_setup/hgnc) and GtoPdb 2026.3.1 (data/db_setup/iuphar).",
           "rules": {"class_hgnc_families": CLASS_FAMS, "class_iuphar_types": sorted(IUPHAR_CLASS_TYPES),
                     "grey_families": GREY_FAMS, "grey_symbol_regex": GREY_SYMBOL.pattern,
                     "control_families": CONTROL_FAMS, "control_exclude_families": sorted(CONTROL_EXCLUDE_FAMS),
                     "control_extra_symbols": sorted(CONTROL_EXTRA_SYMBOLS)},
           "genes": {}}
    for g in sorted(set(cls) | set(grey) | set(ctrl), key=lambda x: int(x.split(":")[1])):
        if g not in genes:
            continue
        lab = "class" if g in cls else ("grey" if g in grey else "control")
        out["genes"][g] = {"symbol": genes[g], "cls": lab, "subclass": sub.get(g) if lab == "class" else None,
                           "group": grey.get(g) if lab == "grey" else ctrl.get(g) if lab == "control" else None}
    (ROOT / "config/db_classes_v1.json").write_text(json.dumps(out, indent=1))
    from collections import Counter
    print(Counter(v["cls"] for v in out["genes"].values()))
    print(Counter(v["subclass"] for v in out["genes"].values() if v["cls"] == "class"))
    print(Counter(v["group"] for v in out["genes"].values() if v["cls"] == "control"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

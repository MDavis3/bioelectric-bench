#!/usr/bin/env python3
"""Q017 setup-only testability count: genes with gain-of-function / dominant-negative alleles, per species x cls.

Reads allele/genotype EXISTENCE only. No phenotype term, qualifier or abnormal/normal field is read anywhere:
  MGI_PhenotypicAllele.rpt  cols 1,4,5,7  (allele id, allele type, allele attributes, marker id)
  MGI_GenePheno.rpt         cols 1,3,7,8  (allelic composition, allele ids, marker ids, genotype id); a row's
                            existence = "genotype has >=1 phenotype record"; the MP column (5) is never touched.
  ZFIN features.txt / genotype_features.txt: scanned only for a dominance / gain-of-function field (none exists).
Groups: units_setup.csv cls via unit_id; genes not in units_setup are classified through the human anchor exactly as
harness/db_build_units.py does (Alliance stringent pairs, fallback HOM/human_orthos, rank class<grey<control), block by
the harness/db_blocks.py rule. cls 'grey' has no schema key and is not reported.
Output: data/db_restricted/reply_q017_testability.json
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_build_units import ROOT, RAW, SETUP, RESTR, tsv, hnum, load_alliance, load_fallback  # noqa: E402

GOF_ATTR = {"Constitutively active", "Gain of function"}
DN_ATTR = {"Dominant negative"}
NULL_ATTR = {"Null/knockout"}


def mouse_genotypes():
    attr, amark = {}, {}
    for r in tsv(RAW / "mgi" / "MGI_PhenotypicAllele.rpt"):
        if len(r) < 7:
            continue
        attr[r[0]] = set(a for a in r[4].split("|") if a)
        amark[r[0]] = r[6]
    present = sorted({a for s in attr.values() for a in s} & (GOF_ATTR | DN_ATTR))
    gof, dn, null = defaultdict(set), defaultdict(set), defaultdict(set)
    for r in tsv(RAW / "mgi" / "MGI_GenePheno.rpt"):
        if len(r) < 8:
            continue
        aids, markers, geno = r[2], r[6], r[7]
        mk = [m for m in markers.split("|") if m]
        if len(mk) != 1:
            continue
        g = mk[0]
        alle = [a for a in aids.split("|") if a and amark.get(a) == g]
        if not alle:
            continue
        ats = [attr.get(a, set()) for a in alle]
        if any(s & GOF_ATTR for s in ats):
            gof[g].add(geno)
        if any(s & DN_ATTR for s in ats):
            dn[g].add(geno)
        if all(s & NULL_ATTR for s in ats):
            null[g].add(geno)
    return gof, dn, null, present


def classifier():
    with open(SETUP / "units_setup.csv", newline="") as fh:
        cur = {r["unit_id"]: (r["cls"], r["block"]) for r in csv.DictReader(fh)}
    classes = json.loads((ROOT / "config" / "db_classes_v1.json").read_text())["genes"]
    human_of = defaultdict(set)
    for a, b in load_alliance():
        for s, t in ((a, b), (b, a)):
            if t.startswith("HGNC:") and not s.startswith("HGNC:"):
                human_of[s].add(t)
    fb = load_fallback()
    fam = defaultdict(set)
    with open(SETUP / "hgnc" / "gene_has_family.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            fam["HGNC:" + r["hgnc_id"]].add(r["family_id"])
    size = defaultdict(int)
    for fs in fam.values():
        for f in fs:
            size[f] += 1
    rank = {"class": 0, "grey": 1, "control": 2}

    def cls_block(species, node):
        uid = f"{species}:{node}"
        if uid in cur:
            return cur[uid]
        hs = human_of.get(node) or fb.get(node, set())
        if not hs:
            return "other", "U" + uid
        best = sorted(hs, key=lambda h: (rank.get((classes.get(h) or {}).get("cls"), 3), hnum(h)))[0]
        c = (classes.get(best) or {}).get("cls")
        c = c if c in rank else "other"
        fs = fam.get(best)
        blk = ("F" + min(fs, key=lambda f: (size[f], int(f)))) if fs else "A" + best
        return c, blk
    return cls_block


def main():
    gof, dn, null, present = mouse_genotypes()
    cls_block = classifier()
    fields = ["n_genes_gof", "n_genes_domneg", "n_genes_gof_or_domneg", "n_genes_null", "n_genes_both_gof_and_null",
              "n_blocks_gof_or_domneg", "n_genotypes_gof_or_domneg", "problem_code"]
    reply = {}
    genes = set(gof) | set(dn) | set(null)
    info = {g: cls_block("mouse", g) for g in genes}
    for c in ("class", "control", "other"):
        sel = {g for g in genes if info[g][0] == c}
        G, D, N = sel & set(gof), sel & set(dn), sel & set(null)
        GD = G | D
        reply["mouse_" + c] = {
            "n_genes_gof": len(G), "n_genes_domneg": len(D), "n_genes_gof_or_domneg": len(GD),
            "n_genes_null": len(N), "n_genes_both_gof_and_null": len(G & N),
            "n_blocks_gof_or_domneg": len({info[g][1] for g in GD}),
            "n_genotypes_gof_or_domneg": len({x for g in GD for x in gof.get(g, set()) | dn.get(g, set())}),
            "problem_code": 0,
        }
    # ZFIN: features.txt / genotype_features.txt carry no dominance or gain-of-function field -> not testable.
    for c in ("class", "control", "other"):
        reply["zebrafish_" + c] = {f: 0 for f in fields[:-1]} | {"problem_code": 1}
    RESTR.mkdir(parents=True, exist_ok=True)
    out = RESTR / "reply_q017_testability.json"
    out.write_text(json.dumps(reply, indent=1) + "\n")
    print("MGI GoF/DN attribute strings present:", present, file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()

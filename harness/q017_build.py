#!/usr/bin/env python3
"""Q017 outcome-side builder (red team spec v1, plans/q017_redteam.md sections 1-9). Run by an outcome-side subagent
only (reads aspect-P annotations). Deterministic.

Inputs   data/raw_db/clinvar/variant_summary.txt.gz, data/raw_db/hpo/phenotype.hpoa, data/db_setup/ontologies/hp.obo,
         data/db_setup/hgnc/*, config/db_classes_v1.json, config/q017_endpoint_map_v1.json,
         config/q017_validation_v1.json, config/q017_cited_cases_v1.json
Outputs  data/db_setup/q017_units_setup.csv          setup columns only (no outcome)
         data/db_restricted/q017_outcome.csv         unit_id, Y_core, Y_roots, Y_exc        (restricted)
         data/db_setup/q017_validation_result.json   labels only
         data/db_setup/q017_outcome.sha256
         data/db_setup/q017_pooled_rate.json         {"Y_core": [n_with, n_units]} over all units pooled
         data/db_restricted/q017_build_counts.json   integer counts (restricted copy of the reply numbers)
         data/db_restricted/q017_resolution.json     how validation / cited entries resolved (restricted; names)

Decisions fixed here (before any outcome was tabulated):
  - Variant rows: Assembly GRCh38; OriginSimple contains "germline" or Origin contains "de novo"; ClinicalSignificance
    exactly Pathogenic | Likely pathogenic | Pathogenic/Likely pathogenic; ReviewStatus in {criteria provided, single
    submitter; criteria provided, multiple submitters, no conflicts; reviewed by expert panel; practice guideline};
    exactly one HGNC_ID and one GeneID (no ";" / "|" / "-1"). Distinct variant = VariationID.
  - Missense: first "(p.Aaa###Bbb)" in Name with Bbb a 3-letter amino acid other than Ter, not "=".
    Nonsense: "(p.Aaa###Ter)". Frameshift: "(p.<...>fs<...>)". Canonical splice: c.###+1/+2/-1/-2 with a single
    position (no range "_"), no protein change in the name or protein change unknown "(p.?)" / absent.
  - Conditions: numeric OMIM ids in PhenotypeIDS (any position of the "|"/"," lists). A unit (gene x OMIM) needs >=1
    OMIM aspect-P hpoa row after dropping qualifier NOT and frequency HP:0040285. Inheritance from aspect-I rows
    (qualifier NOT dropped); dominant = HP:0000006 or HP:0001423 present.
  - n_plp = distinct P/LP variants (passing the row filters, any consequence) for the gene x condition.
  - Terms are resolved through hp.obo alt_id / replaced_by before matching endpoint sets.
  - Y_roots = human ROOTS Y of harness/db_secondary.term_sets("human", ...) on the same hp.obo.
  - Block = smallest HGNC family (fewest genes, ties lowest id) as harness/db_blocks.py; no family -> "A"+HGNC id.
    family_size = largest HGNC family size of the gene, 1 if none.
  - Validation / cited resolution: by gene, then OMIM id if that id is linked to the gene, else by normalised
    condition-name match (hpoa disease_name or ClinVar PhenotypeList), group entries by a fixed name pattern.
"""
import csv
import gzip
import hashlib
import json
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))

CV = ROOT / "data/raw_db/clinvar/variant_summary.txt.gz"
HPOA = ROOT / "data/raw_db/hpo/phenotype.hpoa"
OBO = ROOT / "data/db_setup/ontologies/hp.obo"
SIG = {"Pathogenic", "Likely pathogenic", "Pathogenic/Likely pathogenic"}
REV = {"criteria provided, single submitter", "criteria provided, multiple submitters, no conflicts",
       "reviewed by expert panel", "practice guideline"}
AA = {"Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Pro", "Ser",
      "Thr", "Trp", "Tyr", "Val", "Sec", "Pyl"}
P_RE = re.compile(r"\(p\.([^)]*)\)")
MIS_RE = re.compile(r"^([A-Z][a-z]{2})(\d+)([A-Z][a-z]{2}|=)$")
NON_RE = re.compile(r"^([A-Z][a-z]{2})(\d+)Ter$")
SPL_RE = re.compile(r"c\.(\d+)([+-])([12])(?![\d_])")
DOM = {"HP:0000006", "HP:0001423"}


def consequence(name):
    m = P_RE.search(name)
    p = m.group(1) if m else None
    if p:
        if "fs" in p:
            return "trunc"
        if NON_RE.match(p) and NON_RE.match(p).group(1) in AA:
            return "trunc"
        mm = MIS_RE.match(p)
        if mm and mm.group(1) in AA and mm.group(3) in AA:
            return "mis"
        if p != "?":
            return None
    c = name.split(":", 1)[1] if ":" in name else name
    c = c.split(" ")[0]
    if SPL_RE.match(c) and "_" not in c:
        return "trunc"
    return None


def load_clinvar():
    plp = defaultdict(set)                 # (hgnc, omim) -> variation ids (any consequence)
    mis, trunc = defaultdict(set), defaultdict(set)
    sym, names = {}, defaultdict(set)      # names: (hgnc, omim) -> ClinVar condition names
    n_rows = 0
    with gzip.open(CV, "rt", encoding="utf-8") as fh:
        hdr = fh.readline().lstrip("#").rstrip("\n").split("\t")
        ix = {k: i for i, k in enumerate(hdr)}
        for line in fh:
            r = line.rstrip("\n").split("\t")
            if r[ix["Assembly"]] != "GRCh38" or r[ix["ClinicalSignificance"]] not in SIG:
                continue
            if r[ix["ReviewStatus"]] not in REV:
                continue
            if "germline" not in r[ix["OriginSimple"]] and "de novo" not in r[ix["Origin"]]:
                continue
            h, gid = r[ix["HGNC_ID"]], r[ix["GeneID"]]
            if not h.startswith("HGNC:") or any(x in h + gid for x in (";", "|", ",")) or gid in ("-1", "", "-"):
                continue
            n_rows += 1
            sym[h] = r[ix["GeneSymbol"]]
            vid = r[ix["VariationID"]]
            cons = consequence(r[ix["Name"]])
            pid_groups = r[ix["PhenotypeIDS"]].split("|")
            pl = r[ix["PhenotypeList"]].split("|")
            for gi, grp in enumerate(pid_groups):
                for tok in re.split(r"[,;]", grp):
                    if tok.startswith("OMIM:") and tok[5:].isdigit():
                        k = (h, tok[5:])
                        plp[k].add(vid)
                        if gi < len(pl):
                            names[k].add(pl[gi])
                        if cons == "mis":
                            mis[k].add(vid)
                        elif cons == "trunc":
                            trunc[k].add(vid)
    return plp, mis, trunc, sym, names, n_rows


def load_hpoa(alt, repl, obs):
    from db_secondary import resolve
    P, I, dname = defaultdict(set), defaultdict(set), {}
    with open(HPOA, encoding="utf-8") as fh:
        rows = (l for l in fh if not l.startswith("#"))
        for r in csv.DictReader(rows, delimiter="\t"):
            d = r["database_id"]
            if not d.startswith("OMIM:") or r["qualifier"].strip() == "NOT":
                continue
            mim = d[5:]
            dname[mim] = r["disease_name"]
            if r["aspect"] == "P":
                if r["frequency"].strip() == "HP:0040285":
                    continue
                P[mim].add(resolve(r["hpo_id"], alt, repl, obs) or r["hpo_id"])
            elif r["aspect"] == "I":
                I[mim].add(r["hpo_id"])
    return P, I, dname


def norm(s):
    s = s.lower().replace("type ", "").replace("syndrome", "").replace("-", " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())


def name_match(query, cands):
    q = norm(query)
    qt = set(q.split())
    for c in cands:
        n = norm(c)
        if q and (q in n or n in q):
            return True
        nt = set(n.split())
        nums_q = {t for t in qt if t.isdigit() or len(t) <= 2}
        nums_n = {t for t in nt if t.isdigit() or len(t) <= 2}
        if qt and len(qt & nt) >= max(2, int(0.75 * len(qt))) and nums_q <= nt and (not nums_n or nums_n <= qt | nums_q):
            return True
    return False


GROUPS = {"TRPV4": re.compile(r"dysplasia|brachyolmia|dwarfism|kozlowski|maroteaux|arthropathy|metatropic", re.I),
          "PIEZO2": re.compile(r"arthrogryposis|gordon|marden|walker", re.I)}


def resolve_entry(gene, cname, mim, sym2h, linked, P, dname, cvnames):
    """Return the set of OMIM ids (with >=1 aspect-P row) that the entry resolves to for this gene."""
    h = sym2h.get(gene)
    if not h:
        return h, set()
    mims = {m for (hh, m) in linked if hh == h and m in P}
    def nm(m):
        return [dname.get(m, "")] + sorted(cvnames.get((h, m), ()))
    if mim == "group":
        if cname == "any":
            return h, mims
        pat = GROUPS[gene]
        return h, {m for m in mims if any(pat.search(x) for x in nm(m))}
    if mim in mims and name_match(cname, nm(m=mim)):
        return h, {mim}
    hit = {m for m in mims if name_match(cname, nm(m))}
    if hit:
        return h, hit
    if mim in mims:   # id linked but name differs: accept the id (MIM from memory, name normalisation is coarse)
        return h, {mim}
    return h, set()


def main():
    from db_secondary import parse_obo, term_sets, mouse_label_words
    ch, nmz, alt, repl, obs = parse_obo(OBO)
    Y_roots, _, _, _ = term_sets("human", ch, nmz, mouse_label_words())
    emap = json.loads((ROOT / "config/q017_endpoint_map_v1.json").read_text())
    Ycore, Yexc = set(emap["Y_core_terms"]), set(emap["Y_exc_terms"])
    P, I, dname = load_hpoa(alt, repl, obs)
    plp, mis, trunc, sym, cvnames, n_rows = load_clinvar()
    classes = json.loads((ROOT / "config/db_classes_v1.json").read_text())["genes"]
    hgnc_sym = {}
    with open(ROOT / "data/db_setup/hgnc/hgnc_complete_set.txt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            hgnc_sym[r["symbol"]] = r["hgnc_id"]
    sym2h = dict(hgnc_sym)
    for h, s in sym.items():
        sym2h.setdefault(s, h)
    fam = defaultdict(set)
    for r in csv.DictReader(open(ROOT / "data/db_setup/hgnc/gene_has_family.csv")):
        fam["HGNC:" + r["hgnc_id"]].add(r["family_id"])
    fsize = Counter(f for fs in fam.values() for f in fs)

    def block(h):
        fs = fam.get(h)
        return ("F" + min(fs, key=lambda f: (fsize[f], int(f)))) if fs else "A" + h

    # all gene x condition pairs with an annotated OMIM condition
    label, counts = {}, Counter()
    for k in plp:
        h, m = k
        if m not in P:
            continue
        nm_, nt_ = len(mis.get(k, ())), len(trunc.get(k, ()))
        if nt_ >= 2:
            lab = "LOF"
        elif nm_ >= 3 and nt_ == 0 and I.get(m, set()) & DOM:
            lab = "ALT"
        else:
            lab = "GREY"
        label[k] = lab
        c = classes.get(h, {}).get("cls", "other")
        counts[f"{c}_{lab}"] += 1

    units = [k for k, lab in label.items() if lab != "GREY" and classes.get(k[0], {}).get("cls") in ("class", "control")]
    units.sort(key=lambda k: (int(k[0].split(":")[1]), int(k[1])))
    cell = Counter((k[0], label[k]) for k in units)

    # cited cases
    cited_units, cited_info = set(), []
    cc = json.loads((ROOT / "config/q017_cited_cases_v1.json").read_text())["cases"]
    linked = set(plp)
    for gene, cname, mim in cc:
        h, ms = resolve_entry(gene, cname, mim, sym2h, linked, P, dname, cvnames)
        hit = {(h, m) for m in ms}
        in_setup = hit & set(units)
        cited_units |= in_setup
        cited_info.append({"gene": gene, "entry": cname, "mims": sorted(ms),
                           "labels": [label.get((h, m)) for m in sorted(ms)], "n_setup_units": len(in_setup)})

    # validation (labels only; any class)
    val = json.loads((ROOT / "config/q017_validation_v1.json").read_text())
    vres = {"ALT": [0, 0], "LOF": [0, 0], "unresolved": 0}
    vinfo, vgrey = [], Counter()
    for side, key in (("ALT", "expected_ALT"), ("LOF", "expected_LOF")):
        for gene, cname, mim in val[key]:
            h, ms = resolve_entry(gene, cname, mim, sym2h, linked, P, dname, cvnames)
            if not ms:
                vres["unresolved"] += 1
                vinfo.append({"side": side, "gene": gene, "entry": cname, "resolved": None})
                continue
            # one pair -> one label: if several conditions resolve, take the given MIM if present, else the first
            m = mim if mim in ms else sorted(ms, key=int)[0]
            lab = label[(h, m)]
            vinfo.append({"side": side, "gene": gene, "entry": cname, "resolved": m, "hpoa_name": dname.get(m),
                          "label": lab, "n_mis": len(mis.get((h, m), ())), "n_trunc": len(trunc.get((h, m), ())),
                          "dominant": int(bool(I.get(m, set()) & DOM)), "alternatives": sorted(ms)})
            if lab == "GREY":
                vgrey[side] += 1
                continue
            vres[side][1] += 1
            vres[side][0] += int(lab == side)

    setup_rows, out_rows = [], []
    for k in units:
        h, m = k
        lab = label[k]
        fs = fam.get(h)
        terms = P[m]
        uid = f"{h}|OMIM:{m}"
        setup_rows.append(dict(unit_id=uid, hgnc=h, cls=classes[h]["cls"], block=block(h), label=lab,
                               weight=round(1.0 / cell[(h, lab)], 10), n_terms=len(terms), n_plp=len(plp[k]),
                               family_size=max(fsize[f] for f in fs) if fs else 1, cited=int(k in cited_units)))
        out_rows.append(dict(unit_id=uid, Y_core=int(bool(terms & Ycore)), Y_roots=int(bool(terms & Y_roots)),
                             Y_exc=int(bool(terms & Yexc))))

    def wcsv(path, rows):
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    wcsv(ROOT / "data/db_setup/q017_units_setup.csv", setup_rows)
    op = ROOT / "data/db_restricted/q017_outcome.csv"
    wcsv(op, out_rows)
    (ROOT / "data/db_setup/q017_validation_result.json").write_text(json.dumps(vres, indent=1) + "\n")
    digest = hashlib.sha256(op.read_bytes()).hexdigest()
    (ROOT / "data/db_setup/q017_outcome.sha256").write_text(f"{digest}  data/db_restricted/q017_outcome.csv\n")
    ny = sum(r["Y_core"] for r in out_rows)
    (ROOT / "data/db_setup/q017_pooled_rate.json").write_text(json.dumps({"Y_core": [ny, len(out_rows)]}) + "\n")

    bc = {"rows_kept": n_rows, "pairs_with_P": len(label), **counts,
          "validation_grey_ALT": vgrey["ALT"], "validation_grey_LOF": vgrey["LOF"],
          "cited_entries": len(cc), "cited_entries_resolved": sum(1 for c in cited_info if c["mims"]),
          "cited_entries_in_setup": sum(1 for c in cited_info if c["n_setup_units"]),
          "cited_units": len(cited_units)}
    for c in ("class", "control"):
        for lab in ("ALT", "LOF"):
            sel = [r for r in setup_rows if r["cls"] == c and r["label"] == lab]
            bc[f"{c}_{lab}_units"] = len(sel)
            bc[f"{c}_{lab}_blocks"] = len({r["block"] for r in sel})
    (ROOT / "data/db_restricted/q017_build_counts.json").write_text(json.dumps(bc, indent=1) + "\n")
    (ROOT / "data/db_restricted/q017_resolution.json").write_text(
        json.dumps({"validation": vinfo, "cited": cited_info}, indent=1) + "\n")
    print(json.dumps(bc))
    print(json.dumps(vres))
    return 0


if __name__ == "__main__":
    sys.exit(main())

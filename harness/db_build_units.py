#!/usr/bin/env python3
"""Build gene x species units for the cross-species test (plans/pivot_db_v1.md, sections A-F).

Run by an outcome-side subagent only (reads phenotype files). Deterministic; no network unless the IMPC API
responses are missing (then fetched once, Crawl-Delay honoured, recorded in data/raw_db_manifest.json).

Outputs
  data/db_restricted/units_outcome.csv      unit_id,Y,Y_exc,Y_nosize,lethal_nomorph (planner-denied)
  data/db_restricted/build_counts.json      integer counts by stratum               (planner-denied)
  data/db_setup/units_setup.csv             setup columns only, no outcome     (only with --write-setup)
  data/db_setup/nn_features.jsonl           {"unit_id","mf","expr","grp"}      (only with --write-setup)
  Default run keeps the planner-owned setup files (blocks from harness/db_blocks.py) and reads cls/block from them.
  data/db_setup/db_rates_v1.json            stratum -> [n_units_with_Y, n_units] (all classes pooled)

Decisions beyond the plan text (fixed here, before any outcome was looked at by class):
  - MGI-literature records = MGI_GenePheno rows with >=1 PMID (rows without a PMID are high-throughput IMPC/legacy
    loads; IMPC enters through its own API source).
  - Alliance stringent pair = a row (either direction) with IsBestScore and IsBestRevScore in {Yes, Yes_Adjusted}.
  - Fallback orthology (MGI HOM / ZFIN human_orthos) is used per gene, only for genes with no Alliance stringent human
    ortholog; fallback pairs also join blocks so a unit shares a block with its anchor.
  - ZFIN: entity = affected structure 1 (superterm and subterm); fish with a deficiency/translocation/complex feature
    are excluded (multi-gene); environment must consist only of standard/control conditions (ZECO:0000101/102/103).
  - Expression: the Monarch KG release carries Bgee expressed_in edges only for human and non-MOD species (mouse and
    zebrafish genes appear only as MGI GXD / ZFIN expressed_in edges), so expr = distinct anatomy objects (EMAPA, ZFA,
    UBERON, CL) of biolink:expressed_in edges whose subject is the MGI / ZFIN gene.
  - IMPC: resource IMPC only; tested genes = statistical-result status Successful, non-wildtype zygosity.
"""
import csv
import datetime
import gzip
import hashlib
import json
import os
import sys
import tarfile
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_db"
SETUP = ROOT / "data" / "db_setup"
RESTR = ROOT / "data" / "db_restricted"
IMPC_DIR = RAW / "impc_api"
csv.field_size_limit(1 << 30)

EXCL_EV = {"IMP", "IGI", "IEP"}
STD_ENV = {"ZECO:0000101", "ZECO:0000102", "ZECO:0000103"}
STR_PREFIX = ("ZDB-MRPHLNO", "ZDB-CRISPR", "ZDB-TALEN")
MULTIGENE_FEAT = {"Deficiency", "Translocation", "Complex"}
YES = {"Yes", "Yes_Adjusted"}

UA = "bioelectric-bench-fetch/1.0 (research)"
SOLR = "https://www.ebi.ac.uk/mi/impc/solr/"
IMPC_REQS = [
    ("genotype-phenotype.csv", "genotype-phenotype/select",
     dict(q="*:*", fq="resource_name:IMPC", rows="200000", wt="csv",
          fl="marker_accession_id,mp_term_id,zygosity,phenotyping_center,allele_accession_id,life_stage_name,"
             "resource_name,parameter_stable_id,colony_id")),
    ("statistical-result_tested_genes.json", "statistical-result/select",
     {"q": "*:*", "fq": ["resource_name:IMPC", "status:Successful", "-zygosity:wildtype"], "rows": "0", "wt": "json",
      "facet": "true", "facet.pivot": "marker_accession_id,phenotyping_center", "facet.limit": "-1",
      "facet.mincount": "1"}),
]


def tsv(path, skip_comment=True):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if skip_comment and line.startswith(("#", "!")):
                continue
            yield line.rstrip("\n").split("\t")


def hnum(h):
    return int(h.split(":")[1])


# ---------------------------------------------------------------- IMPC
def fetch_impc():
    IMPC_DIR.mkdir(parents=True, exist_ok=True)
    man_path = ROOT / "data" / "raw_db_manifest.json"
    man = json.loads(man_path.read_text())
    first = True
    for name, path, params in IMPC_REQS:
        if (IMPC_DIR / name).exists():
            continue
        if not first:
            time.sleep(12)
        first = False
        url = SOLR + path + "?" + urllib.parse.urlencode(params, doseq=True)
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=1200).read()
        (IMPC_DIR / name).write_bytes(data)
        row = {"source": "impc_api", "url": url, "local_path": f"data/raw_db/impc_api/{name}", "bytes": len(data),
               "sha256": hashlib.sha256(data).hexdigest(),
               "fetched_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "license": "CC-BY-4.0", "robots_ok": True,
               "note": "IMPC Solr API www.ebi.ac.uk (Crawl-Delay 10 honoured)"}
        man = [r for r in man if r.get("local_path") != row["local_path"]] + [row]
    man_path.write_text(json.dumps(man, indent=1))


def load_impc():
    """-> tested {mgi: center}, records {mgi: [mp,...]}; None if unavailable."""
    try:
        fetch_impc()
    except Exception as e:  # noqa: BLE001
        print("IMPC unavailable:", type(e).__name__, file=sys.stderr)
    gp, sr = IMPC_DIR / IMPC_REQS[0][0], IMPC_DIR / IMPC_REQS[1][0]
    if not (gp.exists() and sr.exists()):
        return None, None
    piv = json.loads(sr.read_text())["facet_counts"]["facet_pivot"]["marker_accession_id,phenotyping_center"]
    tested = {}
    for p in piv:
        cts = sorted(((-c["count"], c["value"]) for c in p.get("pivot", [])))
        tested[p["value"]] = cts[0][1] if cts else "none"
    recs = defaultdict(list)
    gpc = Counter()
    with open(gp, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["zygosity"] not in ("homozygote", "heterozygote", "hemizygote") or not r["marker_accession_id"]:
                continue
            recs[r["marker_accession_id"]].append(r["mp_term_id"])
            gpc[(r["marker_accession_id"], r["phenotyping_center"])] += 1
    for g in recs:  # genes with significant calls but absent from the facet list are tested too
        if g not in tested:
            cts = sorted((-n, c) for (gg, c), n in gpc.items() if gg == g)
            tested[g] = cts[0][1]
    return tested, recs


# ---------------------------------------------------------------- MGI
def load_mgi():
    attr, atype = {}, {}
    for r in tsv(RAW / "mgi" / "MGI_PhenotypicAllele.rpt"):
        if len(r) < 5:
            continue
        attr[r[0]], atype[r[0]] = r[4], r[3]
    genos = defaultdict(set)
    recs = defaultdict(list)
    for r in tsv(RAW / "mgi" / "MGI_GenePheno.rpt"):
        if len(r) < 8:
            continue
        comp, aids, mp, pmids, markers, geno = r[0], r[2], r[4], r[5], r[6], r[7]
        if not pmids.strip():
            continue
        mk = [m for m in markers.split("|") if m]
        if len(mk) != 1 or "Tg(" in comp:
            continue
        alle = [a for a in aids.split("|") if a]
        if not alle:
            continue
        ok = True
        for a in alle:
            at = attr.get(a)
            if at is None or "Null/knockout" not in at or "Recombinase" in at or atype.get(a, "").startswith("Transgenic"):
                ok = False
                break
        if not ok:
            continue
        genos[mk[0]].add(geno)
        recs[mk[0]].append(mp)
    return genos, recs


# ---------------------------------------------------------------- ZFIN
def load_zfin(emap):
    ftype = {r[0]: r[4] for r in tsv(RAW / "zfin" / "features.txt") if len(r) > 4}
    env = defaultdict(set)
    for r in tsv(RAW / "zfin" / "pheno_environment_fish.txt"):
        if len(r) > 2:
            env[r[0]].add(r[2])
    comps = defaultdict(list)
    for r in tsv(RAW / "zfin" / "fish_components_fish.txt"):
        if len(r) > 5:
            comps[r[0]].append((r[2], r[4]))
    fish_gene = {}
    for f, cs in comps.items():
        if any(a.startswith(STR_PREFIX) for _, a in cs):
            continue
        if any(ftype.get(a) in MULTIGENE_FEAT for _, a in cs if a.startswith("ZDB-ALT")):
            continue
        genes = {g for g, _ in cs if g}
        if len(genes) != 1:
            continue
        g = next(iter(genes))
        if not any(gg == g and a.startswith("ZDB-ALT") and ftype.get(a, "") != "Transgenic Insertion" for gg, a in cs):
            continue
        fish_gene[f] = g
    Z = emap["zebrafish"]
    ent, qual, proc, lat = (set(Z[k]) for k in ("entity_terms", "quality_terms", "process_terms",
                                                 "laterality_quality_terms"))
    xent, xproc = set(Z["Y_exc_entity_terms"]), set(Z["Y_exc_process_terms"])
    eexcl, proc_lat, lethq = (set(Z[k]) for k in ("entity_exclude_terms", "process_laterality_only_terms",
                                                  "lethality_quality_terms"))
    go_cc = go_cellular_component()
    fishes = defaultdict(set)
    out = defaultdict(lambda: [0, 0, 0, 0])  # Y, Y_exc, lethal, n_records
    for r in tsv(RAW / "zfin" / "phenotype_fish.txt"):
        if len(r) < 23:
            continue
        g = fish_gene.get(r[0])
        if g is None:
            continue
        e = env.get(r[22])
        if not e or not e <= STD_ENV:
            continue
        fishes[g].add(r[0])
        o = out[g]
        o[3] += 1
        if r[14] != "abnormal":
            continue
        # entity slots: 1 = (subterm r[6], superterm r[10]); 2 = (subterm r[15], superterm r[19])
        e1 = {t for t in (r[6], r[10]) if t}
        terms = e1 | {t for t in (r[15], r[19]) if t}
        q = r[12]
        sub_cc = any(t in go_cc for t in (r[6], r[15]) if t)
        if ((terms & ent and not terms & eexcl and q in qual and not sub_cc) or (terms & proc)
                or (terms & proc_lat and q in lat) or q in lat):
            o[0] = 1
        if e1 & xent or e1 & xproc:
            o[1] = 1
        if q in lethq:
            o[2] = 1
    return fishes, out


def go_cellular_component():
    cc, cur = set(), None
    with open(SETUP / "ontologies" / "go-basic.obo", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("id: GO:"):
                cur = line[4:].strip()
            elif line.startswith("namespace: cellular_component") and cur:
                cc.add(cur)
            elif line.startswith("[Term]"):
                cur = None
    return cc


# ---------------------------------------------------------------- orthology, families, GO, expression
def load_alliance():
    pairs = set()
    for r in tsv(RAW / "alliance" / "ORTHOLOGY-ALLIANCE_COMBINED.tsv.gz"):
        if len(r) < 13 or r[0] == "Gene1ID":
            continue
        a, b = r[0], r[4]
        if not (a.startswith(("HGNC:", "MGI:", "ZFIN:")) and b.startswith(("HGNC:", "MGI:", "ZFIN:"))):
            continue
        if a.split(":")[0] == b.split(":")[0]:
            continue
        if r[11] in YES and r[12] in YES:
            pairs.add(tuple(sorted((a, b))))
    return pairs


def load_fallback():
    fb = defaultdict(set)
    grp = defaultdict(lambda: ([], []))
    for r in tsv(RAW / "mgi" / "HOM_MouseHumanSequence.rpt"):
        if len(r) < 7 or r[0] == "DB Class Key":
            continue
        if r[2] == "10090" and r[5]:
            grp[r[0]][0].append(r[5])
        elif r[2] == "9606" and r[6]:
            grp[r[0]][1].append(r[6])
    for ms, hs in grp.values():
        for m in ms:
            fb[m].update(hs)
    for r in tsv(RAW / "zfin" / "human_orthos.txt"):
        if len(r) > 7 and r[7].strip().isdigit():
            fb["ZFIN:" + r[0]].add("HGNC:" + r[7].strip())
    return fb


def load_families():
    fam = defaultdict(set)
    with open(SETUP / "hgnc" / "gene_has_family.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            fam["HGNC:" + r["hgnc_id"]].add(r["family_id"])
    size = Counter(f for fs in fam.values() for f in fs)
    return fam, size


def load_uniprot_map():
    u2h = defaultdict(set)
    with open(SETUP / "hgnc" / "hgnc_complete_set.txt", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            for u in (r.get("uniprot_ids") or "").replace('"', "").split("|"):
                if u:
                    u2h[u].add(r["hgnc_id"])
    return u2h


def load_gaf(path, idmap=None):
    """-> pmids {id: set}, mf {id: set}. idmap maps column-2 ids to output ids (set)."""
    pm, mf = defaultdict(set), defaultdict(set)
    for r in tsv(path):
        if len(r) < 9 or r[6] in EXCL_EV:
            continue
        ids = idmap.get(r[1], ()) if idmap is not None else (r[1],)
        if not ids:
            continue
        refs = [x for x in r[5].split("|") if x.startswith("PMID:")]
        for i in ids:
            pm[i].update(refs)
            if r[8] == "F" and "NOT" not in r[3]:
                mf[i].add(r[4])
    return pm, mf


def load_expression():
    cache = RESTR / "monarch" / "expressed_in_edges.tsv"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(RAW / "monarch" / "monarch-kg.tar.gz") as tf:
            m = next(x for x in tf.getmembers() if x.name.endswith("edges.tsv"))
            fh = tf.extractfile(m)
            hdr = fh.readline().decode().rstrip("\n").split("\t")
            ip, iks, isu, iob = (hdr.index(k) for k in ("predicate", "primary_knowledge_source", "subject", "object"))
            with open(cache, "w") as out:
                out.write("predicate\tprimary_knowledge_source\tsubject\tobject\n")
                for line in fh:
                    if b"expressed_in" not in line:
                        continue
                    r = line.decode().rstrip("\n").split("\t")
                    if "expressed_in" in r[ip]:
                        out.write(f"{r[ip]}\t{r[iks]}\t{r[isu]}\t{r[iob]}\n")
    ex = defaultdict(set)
    for r in tsv(cache):
        if r[0] == "predicate" or len(r) < 4:
            continue
        s = r[2]
        if s.startswith(("MGI:", "ZFIN:")) and r[3].startswith(("EMAPA:", "ZFA:", "UBERON:", "CL:")):
            ex[s].add(r[3])
    return ex


# ---------------------------------------------------------------- main
class DSU:
    def __init__(self):
        self.p = {}

    def find(self, x):
        p = self.p
        p.setdefault(x, x)
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            if rb < ra:
                ra, rb = rb, ra
            self.p[rb] = ra


def main():
    emap = json.loads((ROOT / "config" / "db_endpoint_map_v1.json").read_text())
    classes = json.loads((ROOT / "config" / "db_classes_v1.json").read_text())["genes"]
    M = emap["mouse"]
    mY, mX, mL = set(M["Y_terms"]), set(M["Y_exc_terms"]), set(M["lethality_terms"])
    mN = set(M["Y_terms_nosize_secondary"])

    mgi_genos, mgi_recs = load_mgi()
    impc_tested, impc_recs = load_impc()
    impc_ok = impc_tested is not None
    impc_tested = impc_tested or {}
    impc_recs = impc_recs or {}
    z_fish, z_out = load_zfin(emap)

    units = {}  # unit_id -> dict
    for g in sorted(set(mgi_genos) | set(impc_tested)):
        recs = mgi_recs.get(g, []) + impc_recs.get(g, [])
        y, x, l, yn = (int(any(t in S for t in recs)) for S in (mY, mX, mL, mN))
        units["mouse:" + g] = dict(species="mouse", node=g, src_mgi=int(g in mgi_genos), src_impc=int(g in impc_tested),
                                   src_zfin=0, impc_center=impc_tested.get(g, ""), n_rec=len(recs),
                                   n_genotypes=len(mgi_genos.get(g, ())) + int(g in impc_tested),
                                   Y=y, Y_exc=x, lethal=l, Y_nosize=yn)
    for g in sorted(z_fish):
        y, x, l, n = z_out[g]
        units["zebrafish:" + g] = dict(species="zebrafish", node="ZFIN:" + g, src_mgi=0, src_impc=0, src_zfin=1,
                                       impc_center="", n_rec=n, n_genotypes=len(z_fish[g]), Y=y, Y_exc=x, lethal=l,
                                       Y_nosize=y)

    # orthology and anchors
    pairs = load_alliance()
    human_of = defaultdict(set)
    for a, b in pairs:
        for s, t in ((a, b), (b, a)):
            if t.startswith("HGNC:") and not s.startswith("HGNC:"):
                human_of[s].add(t)
    fb = load_fallback()
    fb_pairs = set()
    rank = {"class": 0, "grey": 1, "control": 2}
    for u in units.values():
        hs = human_of.get(u["node"])
        if not hs:
            hs = fb.get(u["node"], set())
            fb_pairs.update((u["node"], h) for h in hs)
        if not hs:
            u.update(anchor="", cls="other", subclass="")
            continue
        best = sorted(hs, key=lambda h: (rank.get((classes.get(h) or {}).get("cls"), 3), hnum(h)))[0]
        c = classes.get(best) or {}
        u.update(anchor=best, cls=c.get("cls") if c.get("cls") in rank else "other",
                 subclass=(c.get("subclass") or "") if c.get("cls") == "class" else "")

    # blocks
    fam, fsize = load_families()
    dsu = DSU()
    for a, b in pairs | fb_pairs:
        dsu.union(a, b)
    for h, fs in fam.items():
        for f in fs:
            dsu.union(h, "FAM:" + f)
    for u in units.values():
        dsu.find(u["node"])
    comp_min = {}
    for x in list(dsu.p):
        if x.startswith("FAM:"):
            continue
        r = dsu.find(x)
        if r not in comp_min or x < comp_min[r]:
            comp_min[r] = x
    for u in units.values():
        u["block"] = "B" + comp_min[dsu.find(u["node"])]

    # covariates and NN features
    u2h = load_uniprot_map()
    h_pm, h_mf = load_gaf(SETUP / "go" / "goa_human.gaf.gz", u2h)
    m_pm, m_mf = load_gaf(SETUP / "go" / "mgi.gaf.gz")
    z_pm, z_mf = load_gaf(SETUP / "go" / "zfin.gaf.gz")
    expr = load_expression()
    feats = []
    for uid in sorted(units):
        u = units[uid]
        if u["anchor"]:
            pm, mf = h_pm.get(u["anchor"], set()), h_mf.get(u["anchor"], set())
        elif u["species"] == "mouse":
            pm, mf = m_pm.get(u["node"], set()), m_mf.get(u["node"], set())
        else:
            g = u["node"][5:]
            pm, mf = z_pm.get(g, set()), z_mf.get(g, set())
        fs = sorted(fam.get(u["anchor"], ()), key=int) if u["anchor"] else []
        ex = sorted(expr.get(u["node"], ()))
        u.update(depth=len(pm), family_size=max([fsize[f] for f in fs] or [1]), expr_breadth=len(ex))
        feats.append({"unit_id": uid, "mf": sorted(mf), "expr": ex, "grp": fs})

    # write
    RESTR.mkdir(parents=True, exist_ok=True)
    SETUP.mkdir(parents=True, exist_ok=True)
    cols = ["unit_id", "species", "anchor", "cls", "subclass", "block", "src_mgi", "src_impc", "src_zfin",
            "impc_center", "depth", "n_genotypes", "family_size", "expr_breadth"]
    mismatch = False
    if "--write-setup" in sys.argv:
        with open(SETUP / "units_setup.csv", "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(cols)
            for uid in sorted(units):
                u = units[uid]
                w.writerow([uid] + [u[c] for c in cols[1:]])
        with open(SETUP / "nn_features.jsonl", "w") as fh:
            for f in feats:
                fh.write(json.dumps(f) + "\n")
    else:
        # default: setup files are owned by the planner (blocks rewritten by harness/db_blocks.py); keep them and
        # take the unit set, cls and block from the current setup table.
        with open(SETUP / "units_setup.csv", newline="") as fh:
            cur = {r["unit_id"]: r for r in csv.DictReader(fh)}
        mismatch = set(cur) != set(units)
        for uid, u in units.items():
            if uid in cur:
                u.update(cls=cur[uid]["cls"], block=cur[uid]["block"])
    with open(RESTR / "units_outcome.csv", "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["unit_id", "Y", "Y_exc", "Y_nosize", "lethal_nomorph"])
        for uid in sorted(units):
            u = units[uid]
            w.writerow([uid, u["Y"], u["Y_exc"], u["Y_nosize"], int(u["lethal"] and not u["Y"])])
    rates = defaultdict(lambda: [0, 0])
    for u in units.values():
        st = f'{u["species"]}|{u["src_mgi"]}{u["src_impc"]}{u["src_zfin"]}'
        rates[st][0] += u["Y"]
        rates[st][1] += 1
    (SETUP / "db_rates_v1.json").write_text(json.dumps(dict(sorted(rates.items())), indent=1) + "\n")

    # integer reply counts
    keymap = {"mouse|100": "mouse_mgi_only", "mouse|010": "mouse_impc_only", "mouse|110": "mouse_mgi_and_impc",
              "zebrafish|001": "zebrafish_zfin"}
    reply = {}
    for key in list(keymap.values()) + ["all"]:
        sel = [u for u in units.values()
               if key == "all" or keymap.get(f'{u["species"]}|{u["src_mgi"]}{u["src_impc"]}{u["src_zfin"]}') == key]
        cl = Counter(u["cls"] for u in sel)
        reply[key] = {
            "n_units": len(sel), "n_class": cl["class"], "n_control": cl["control"], "n_grey": cl["grey"],
            "n_other": cl["other"],
            "n_class_blocks": len({u["block"] for u in sel if u["cls"] == "class"}),
            "n_control_blocks": len({u["block"] for u in sel if u["cls"] == "control"}),
            "n_blocks": len({u["block"] for u in sel}),
            "n_Y_all_genes": sum(u["Y"] for u in sel),
            "n_eligible_records": sum(u["n_rec"] for u in sel),
            "n_no_human_anchor": sum(1 for u in sel if not u["anchor"]),
            "problem_code": 1 if (not impc_ok and key.startswith("mouse_")) else (2 if mismatch else 0),
        }
    (RESTR / "reply_db_build.json").write_text(json.dumps(reply, indent=1) + "\n")
    print(f"units={len(units)} impc_ok={int(impc_ok)}")


if __name__ == "__main__":
    main()

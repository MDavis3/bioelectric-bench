#!/usr/bin/env python3
"""EXPLORATORY secondary analyses after the counted database test (plans/pivot_db_v1.md section J; queue Q012, Q013).
Nothing here can change the sealed verdict in reports/db_counted_v1.json. Sealed code and config are imported, never
edited.

Task A (Q013, zebrafish morpholino artefact)
  Morphant unit = ZFIN gene with >=1 fish that carries exactly one sequence-targeting reagent, that reagent is a
  morpholino (ZDB-MRPHLNO) whose Morpholinos.txt target list is exactly that one gene, no CRISPR/TALEN, no genomic
  feature other than transgenic insertions (reporter backgrounds allowed; no mutant allele, deficiency or
  translocation), and >=1 phenotype record in a standard-only environment (ZECO:0000101/102/103). Y, Y_exc and
  lethality use the sealed zebrafish record rules of harness/db_build_units.load_zfin verbatim (copied loop, same
  term sets from config/db_endpoint_map_v1.json). Anchor, class, block (smallest HGNC family of the anchor, rule of
  harness/db_blocks.py), depth, family size and expression breadth follow harness/db_build_units.py; n_genotypes =
  number of eligible morphant fish. Paired comparison with the sealed mutant units (data/db_restricted/
  units_outcome.csv) by gene; McNemar exact (binomial on discordant pairs). T1-style adjusted OR on morphant units with
  harness/dbtest.py design + out-of-fold NN score (same k, shrink, folds rule) via harness/db_explore.t1_block.

Task B (Q012, secondary species): Xenopus (Xenbase GenePhenoRef), fly (FlyBase genotype_phenotype_data), human (HPO
  genes_to_phenotype). Endpoint choices (documented in ROOTS below):
  - "native" endpoint per species: include roots analogous to the sealed mouse/zebrafish roots (axial skeleton,
    craniofacial/head, limb/appendage, laterality, somite/segmentation, body axes, gastrulation, neural tube, notochord,
    neural crest migration, pharyngeal arch, tail), closure in the species ontology, minus closures of the same
    excluded areas as mouse (nervous system, behaviour, cardiovascular except laterality/looping, muscle, eye, ear,
    pigmentation, metabolism/homeostasis, growth, mortality), plus the mouse label-word exclusion list per term
    (Xenopus and fly: without the word "size", because XPO writes "small X" as "decreased size of the X" where MP keeps
    "small X"; human: verbatim).
  - "upheno" endpoint: a record counts when its term has a uPheno cross-species exact match (direct, or via a shared
    UPHENO class, data/raw_db/monarch/upheno-*.sssom.tsv) to an MP term in the sealed mouse Y set (Y_exc: mouse Y_exc
    set). Only terms with an MP equivalent can count; coverage is reported. Fly anatomy (FBbt) has no uPheno match.
  - Y_exc analogues: nervous system, behaviour, cardiovascular, muscle, ear (fly: nervous system, neurons, glia,
    muscle, dorsal vessel, FBcv behaviour/neuro classes), minus laterality / neural tube exceptions as in mouse.
  Units: Xenopus = Xenbase gene page (X. laevis .L/.S and X. tropicalis pooled); all records (GenePhenoRef carries no
  reagent column, so morpholino vs mutant vs overexpression is NOT detectable; flag recorded as unknown). Fly = FBgn
  with >=1 genotype whose components are all classical/insertion alleles (FBal) of that one gene with an allele class
  amorphic / hypomorphic / loss of function (no antimorphic, neomorphic, hypermorphic, gain of function, wild-type;
  no aberrations FBab; alleles carrying an encoded product/tool excluded). Human = HGNC gene in genes_to_phenotype
  (disease-gene level; any variant mechanism).
  Anchor: Alliance stringent pair (IsBestScore and IsBestRevScore in Yes/Yes_Adjusted); fallback per gene (only when
  no Alliance stringent human ortholog): FlyBase dmel_human_orthologs (all listed HGNC), Xenbase
  XenbaseGeneHumanOrthologMapping (Entrez -> HGNC). Best anchor = class > grey > control > other, then lowest HGNC
  number (db_build_units rule). Block = smallest HGNC family of the anchor (db_blocks rule).
  Adjusted OR: logistic regression of Y on class (vs control) + z(log1p GO-PMID depth of anchor) + z(log1p family
  size); no annotation-count covariate, no NN score. Block bootstrap (1000) percentile CI; block permutation (1000,
  one-sided, x permuted at block level within depth-tertile strata; dbtest.block_table / block_perm_x).

  python harness/db_secondary.py            -> reports/db_secondary_v1.json, reports/db_secondary_v1.md
"""
import csv
import gzip
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import binomtest, fisher_exact

sys.path.insert(0, str(Path(__file__).resolve().parent))
import db_build_units as B  # noqa: E402
import db_explore as X  # noqa: E402
import dbtest as D  # noqa: E402

ROOT = D.ROOT
RAW = ROOT / "data/raw_db"
ONT = ROOT / "data/db_setup/ontologies"
N_BOOT = N_PERM = 1000
SIZE_WORDS = ("small", "short", "long", "large", "enlarged", "elongated", "size", "length", "width", "height",
              "macro", "micro", "hypoplas", "hyperplas", "aplasia", "decreased", "increased", "thin", "thick")

ROOTS = {
    "human": {
        "include": ["HP:0009121", "HP:0000772", "HP:0000766", "HP:0030853", "HP:0001696", "HP:0031592", "HP:0001651",
                    "HP:0011544", "HP:0045005", "HP:0410043", "HP:0000234", "HP:0040064", "HP:0011844", "HP:0002644",
                    "HP:0000782", "HP:0000889", "HP:0005107"],
        "exclude": ["HP:0000707", "HP:0001626", "HP:0003011", "HP:0000478", "HP:0000598", "HP:0001574", "HP:0001939",
                    "HP:0040006", "HP:0001507", "HP:0000818"],
        "exclude_keep": ["HP:0030853", "HP:0001696", "HP:0031592", "HP:0001651", "HP:0011544", "HP:0045005",
                         "HP:0410043"],
        "exclude_extra": ["HP:0010674", "HP:0000682", "HP:0011073", "HP:0006292", "HP:0000157", "HP:0011830"],
        "exc": ["HP:0000707", "HP:0001626", "HP:0003011", "HP:0000598"],
        "exc_minus": ["HP:0030853", "HP:0001696", "HP:0031592", "HP:0001651", "HP:0011544", "HP:0045005",
                      "HP:0410043"],
        "label_words": "mouse list verbatim",
    },
    "xenopus": {
        "include": ["XPO:0100325", "XPO:0107262", "XPO:0101439", "XPO:0100905", "XPO:0100166", "XPO:0107260",
                    "XPO:0107261", "XPO:0142056", "XPO:0115386", "XPO:0115384", "XPO:0100741", "XPO:0100136",
                    "XPO:0100677", "XPO:0100422", "XPO:0100513", "XPO:0101102", "XPO:0100461", "XPO:0100002",
                    "XPO:0100591", "XPO:0100296", "XPO:0100758", "XPO:0100386", "XPO:0100466", "XPO:0100305",
                    "XPO:0100768", "XPO:0100123", "XPO:0100764", "XPO:0101040"],
        # XPO process terms sit flat under 'abnormal biological process' (XPO:0116434); included by label pattern
        "process_root": "XPO:0116434",
        "process_include_regex": r"left/right|left-right|axis|gastrulation|somit|segmentation|convergent extension|"
                                 r"neural tube|neural crest|neural fold|notochord|heart looping|dorsal/ventral|"
                                 r"anterior/posterior|blastopore|pattern specification|limb (development|morphogenesis)|"
                                 r"craniofacial|pharyngeal arch|tail bud|embryonic skeletal",
        "process_exc_regex": r"heart|cardiac|neur|nerv|muscle|synap|behavio|swimming|action potential|sensory|"
                             r"vision|visual|hearing|otic",
        "process_exc_keep_regex": r"heart looping|left/right|left-right|neural tube|neural crest|neural fold",
        "exclude": ["XPO:0100032", "XPO:0100363", "XPO:0100013", "XPO:0100468", "XPO:0100185", "XPO:0100273",
                    "XPO:0100536", "XPO:0100995", "XPO:0100497", "XPO:0100734", "XPO:0101278", "XPO:0101387",
                    "XPO:0116429", "XPO:0115505"],
        "exclude_keep": ["XPO:0100136", "XPO:0100166"],
        # obsolete XPO ids without replaced_by, mapped by hand (axis duplication)
        "obsolete_map": {"XPO:0115824": "XPO:0141924", "XPO:0115825": "XPO:0141924"},
        "exc": ["XPO:0100032", "XPO:0100363", "XPO:0100468", "XPO:0100536", "XPO:0100995", "XPO:0100497",
                "XPO:0100734", "XPO:0116429"],
        "exc_minus": ["XPO:0100136", "XPO:0100677", "XPO:0107262", "XPO:0101439"],
        "label_words": "mouse list without 'size'",
    },
    "fly": {
        "include": ["FBcv:0000698", "FBcv:0000686", "FBcv:0000324", "FBcv:0000449", "FBcv:0000316",
                    "FBbt:00004729", "FBbt:00001778", "FBbt:00004640", "FBbt:00001780", "FBbt:00004783",
                    "FBbt:00001779", "FBbt:00001766", "FBbt:00000154", "FBbt:00004984", "FBbt:00005201"],
        "exclude": ["FBbt:00005093", "FBbt:00005106", "FBbt:00005144", "FBbt:00005074", "FBbt:00058111",
                    "FBbt:00058291", "FBbt:00004508"],
        "exclude_keep": [],
        "exc": ["FBbt:00005093", "FBbt:00005106", "FBbt:00005144", "FBbt:00005074", "FBbt:00058111",
                "FBbt:00058291", "FBcv:0000387", "FBcv:0000434", "FBcv:0000435", "FBcv:0000389", "FBcv:0000417",
                "FBcv:0000418"],
        "exc_minus": ["FBbt:00004508"],  # mouse Y_exc has no eye/vision; fly adult eye is part of the nervous system
        "label_words": "mouse list without 'size'",
        "variant_with_adult_eye": "Y_eye: same as Y but FBbt:00004508 (adult eye) and its parts not excluded",
    },
}


# ---------------------------------------------------------------- ontology helpers

def parse_obo(path, rels=("is_a",)):
    children, names, alt, repl, obs = defaultdict(set), {}, {}, {}, set()
    cur = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("["):
                cur = "" if line == "[Term]" else None
                continue
            if cur is None:
                continue
            if line.startswith("id: "):
                cur = line[4:]
            elif not cur:
                continue
            elif line.startswith("name: "):
                names[cur] = line[6:]
            elif line.startswith("alt_id: "):
                alt[line[8:].split(" ")[0]] = cur
            elif line.startswith("replaced_by: "):
                repl[cur] = line[13:].split(" ")[0]
            elif line.startswith("is_obsolete: true"):
                obs.add(cur)
            elif line.startswith("is_a: ") and "is_a" in rels:
                children[line[6:].split(" ")[0]].add(cur)
            elif line.startswith(("relationship: part_of ", "relationship: BFO:0000050 ")) and "part_of" in rels:
                children[line.split(" ")[2]].add(cur)
    return children, names, alt, repl, obs


def closure(roots, children):
    out, stack = set(), list(roots)
    while stack:
        t = stack.pop()
        if t in out:
            continue
        out.add(t)
        stack.extend(children.get(t, ()))
    return out


def resolve(t, alt, repl, obs):
    t = alt.get(t, t)
    seen = 0
    while t in obs and t in repl and seen < 5:
        t, seen = repl[t], seen + 1
    return None if t in obs else t


def term_sets(sp, ch, nm, words):
    R = ROOTS[sp]
    inc = closure(R["include"], ch)
    exc = (closure(R["exclude"], ch) - closure(R["exclude_keep"], ch)) | closure(R.get("exclude_extra", []), ch)
    lw = lambda t: any(w in nm.get(t, "").lower() for w in words)
    y = {t for t in inc - exc if not lw(t)}
    yx = closure(R["exc"], ch) - closure(R["exc_minus"], ch)
    if sp == "xenopus":
        procs = closure([R["process_root"]], ch)
        inc_re, exc_re, keep_re = (re.compile(R[k], re.I) for k in
                                   ("process_include_regex", "process_exc_regex", "process_exc_keep_regex"))
        for t in procs:
            n = nm.get(t, "")
            if inc_re.search(n) and not lw(t) and not (exc_re.search(n) and not keep_re.search(n)):
                y.add(t)
            if exc_re.search(n) and not keep_re.search(n):
                yx.add(t)
    extra = {}
    if sp == "fly":
        exc2 = closure([t for t in R["exclude"] if t != "FBbt:00004508"], ch)
        extra["Y_eye"] = {t for t in inc | closure(["FBbt:00004508"], ch) if t not in exc2 and not lw(t)}
    nosize = {t for t in y if not any(w in nm.get(t, "").lower() for w in SIZE_WORDS)}
    return y, yx, nosize, extra


def mouse_label_words():
    return json.loads((ROOT / "config/db_endpoint_roots_v1.json").read_text())["mouse"]["Y_exclude_label_words"]


def upheno_map():
    """species term -> set of MP terms (crossSpeciesExactMatch, direct or via a shared UPHENO class)."""
    pair = defaultdict(set)
    for f in ("upheno-cross-species.sssom.tsv", "upheno-species-independent.sssom.tsv"):
        hdr = None
        with open(RAW / "monarch" / f, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    continue
                r = line.rstrip("\n").split("\t")
                if hdr is None:
                    hdr = {k: i for i, k in enumerate(r)}
                    continue
                if "ExactMatch" not in r[hdr["predicate_id"]]:
                    continue
                a, b = r[hdr["subject_id"]], r[hdr["object_id"]]
                pair[a].add(b)
                pair[b].add(a)
    out = defaultdict(set)
    for t, ns in pair.items():
        if t.startswith(("MP:", "UPHENO:")):
            continue
        for n in ns:
            if n.startswith("MP:"):
                out[t].add(n)
            elif n.startswith("UPHENO:"):
                out[t].update(m for m in pair[n] if m.startswith("MP:"))
    return out


# ---------------------------------------------------------------- shared gene-level helpers

class Ctx:
    def __init__(self):
        self.classes = json.loads((ROOT / "config/db_classes_v1.json").read_text())["genes"]
        self.fam, self.fsize = B.load_families()
        u2h = B.load_uniprot_map()
        self.h_pm, self.h_mf = B.load_gaf(ROOT / "data/db_setup/go/goa_human.gaf.gz", u2h)
        self.entrez = {}
        self.symbol = {}
        with open(ROOT / "data/db_setup/hgnc/hgnc_complete_set.txt", newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                if r.get("entrez_id"):
                    self.entrez[r["entrez_id"].strip()] = r["hgnc_id"]
                self.symbol[r["hgnc_id"]] = r["symbol"]
        self.alliance = self._alliance()

    def _alliance(self):
        """non-human gene id -> set(HGNC) from stringent Alliance pairs (any species)."""
        out = defaultdict(set)
        for r in B.tsv(RAW / "alliance/ORTHOLOGY-ALLIANCE_COMBINED.tsv.gz"):
            if len(r) < 13 or r[0] == "Gene1ID":
                continue
            a, b = r[0], r[4]
            if r[11] not in B.YES or r[12] not in B.YES:
                continue
            if b.startswith("HGNC:") and not a.startswith("HGNC:"):
                out[a].add(b)
            elif a.startswith("HGNC:") and not b.startswith("HGNC:"):
                out[b].add(a)
        return out

    def best(self, hs):
        rank = {"class": 0, "grey": 1, "control": 2}
        if not hs:
            return "", "other", ""
        h = sorted(hs, key=lambda h: (rank.get((self.classes.get(h) or {}).get("cls"), 3), B.hnum(h)))[0]
        c = self.classes.get(h) or {}
        cls = c.get("cls") if c.get("cls") in rank else "other"
        return h, cls, (c.get("subclass") or "") if cls == "class" else ""

    def block(self, anchor, uid):
        if not anchor:
            return "U" + uid
        fs = self.fam.get(anchor)
        if not fs:
            return "A" + anchor
        return "F" + min(fs, key=lambda f: (self.fsize[f], int(f)))

    def covs(self, anchor):
        fs = self.fam.get(anchor, ()) if anchor else ()
        return len(self.h_pm.get(anchor, ())) if anchor else 0, max([self.fsize[f] for f in fs] or [1])


# ---------------------------------------------------------------- statistics

def zlog(v):
    v = np.log1p(np.asarray(v, float))
    sd = v.std() or 1.0
    return (v - v.mean()) / sd


def t1_simple(s, E, x, y, cc, rng, n_boot=N_BOOT, n_perm=N_PERM):
    """Adjusted log OR for x (class vs control) with covariates E only; block bootstrap CI and block permutation."""
    if x[cc].sum() < 5 or (1 - x[cc]).sum() < 5 or y[cc].sum() == 0:
        return {"or": None, "note": "too few units or no events", "n_x1": int(x[cc].sum()), "n_x0": int((1 - x[cc]).sum())}
    fit = lambda xx, sel: D.logit_fit(np.column_stack([xx[sel], E[sel]]), y[sel])[1]
    b = fit(x, cc)
    blocks = np.unique(s.block.values[cc])
    bidx = {bk: np.where((s.block.values == bk) & cc)[0] for bk in blocks}
    boots = []
    for _ in range(n_boot):
        sel = np.concatenate([bidx[bk] for bk in rng.choice(blocks, len(blocks), replace=True)])
        if x[sel].min() != x[sel].max() and y[sel].max() > 0:
            boots.append(D.logit_fit(np.column_stack([x[sel], E[sel]]), y[sel])[1])
    table = D.block_table(s, x, cc)
    perms = np.array([fit(D.block_perm_x(s, x, cc, rng, table), cc) for _ in range(n_perm)])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"or": round(math.exp(b), 3), "lo": round(math.exp(lo), 3), "hi": round(math.exp(hi), 3),
            "perm_p_one_sided": round((1 + np.sum(perms >= b)) / (1 + n_perm), 4),
            "perm_p_two_sided": round((1 + np.sum(np.abs(perms - np.median(perms)) >= abs(b - np.median(perms))))
                                      / (1 + n_perm), 4),
            "n_x1": int(x[cc].sum()), "n_x0": int((1 - x[cc]).sum()),
            "n_x1_blocks": int(len(np.unique(s.block.values[cc & (x == 1)]))), "boot_used": len(boots)}


def crude(df, cols):
    out = {}
    for c in ("class", "control", "grey", "other"):
        m = df.cls == c
        out[c] = {"n": int(m.sum())}
        for col in cols:
            out[c][col + "_rate"] = round(float(df.loc[m, col].mean()), 3) if m.any() else None
            out[c]["n_" + col] = int(df.loc[m, col].sum())
    cc = df[df.cls.isin(["class", "control"])]
    for col in cols:
        t = pd.crosstab(cc.cls == "class", cc[col]).reindex(index=[True, False], columns=[1, 0], fill_value=0).values
        orr, p = fisher_exact(t)
        out[f"crude_or_{col}"] = {"or": round(float(orr), 3) if np.isfinite(orr) else None, "fisher_p": float(f"{p:.3g}")}
    return out


def species_analysis(df, ycols, seed):
    """df: unit table with cls, block, depth, family_size and outcome columns."""
    s = df.reset_index(drop=True).copy()
    s["stratum"] = "one"
    E = np.column_stack([zlog(s.depth), zlog(s.family_size)])
    x = (s.cls == "class").astype(float).values
    cc = s.cls.isin(["class", "control"]).values
    rng = np.random.default_rng(seed)
    res = {"n_units": len(s), "n_class": int((s.cls == "class").sum()), "n_control": int((s.cls == "control").sum()),
           "n_grey": int((s.cls == "grey").sum()), "n_other": int((s.cls == "other").sum()),
           "n_class_blocks": int(s[s.cls == "class"].block.nunique()),
           "n_control_blocks": int(s[s.cls == "control"].block.nunique()),
           "crude": crude(s, ycols), "adjusted": {},
           "median_n_records": {c: float(s.loc[s.cls == c, "n_rec"].median()) for c in ("class", "control")
                                if (s.cls == c).any()}}
    for col in ycols:
        res["adjusted"][col] = t1_simple(s, E, x, s[col].values.astype(float), cc, rng)
    return res


# ---------------------------------------------------------------- Task A: zebrafish morphants

def zfin_records(fish_gene, emap):
    """Verbatim copy of the record loop of harness/db_build_units.load_zfin for an arbitrary fish -> gene map."""
    env = defaultdict(set)
    for r in B.tsv(RAW / "zfin/pheno_environment_fish.txt"):
        if len(r) > 2:
            env[r[0]].add(r[2])
    Z = emap["zebrafish"]
    ent, qual, proc, lat = (set(Z[k]) for k in ("entity_terms", "quality_terms", "process_terms",
                                                 "laterality_quality_terms"))
    xent, xproc = set(Z["Y_exc_entity_terms"]), set(Z["Y_exc_process_terms"])
    eexcl, proc_lat, lethq = (set(Z[k]) for k in ("entity_exclude_terms", "process_laterality_only_terms",
                                                  "lethality_quality_terms"))
    go_cc = B.go_cellular_component()
    fishes = defaultdict(set)
    out = defaultdict(lambda: [0, 0, 0, 0])
    for r in B.tsv(RAW / "zfin/phenotype_fish.txt"):
        if len(r) < 23:
            continue
        g = fish_gene.get(r[0])
        if g is None:
            continue
        e = env.get(r[22])
        if not e or not e <= B.STD_ENV:
            continue
        fishes[g].add(r[0])
        o = out[g]
        o[3] += 1
        if r[14] != "abnormal":
            continue
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


def morphant_fish():
    ftype = {r[0]: r[4] for r in B.tsv(RAW / "zfin/features.txt") if len(r) > 4}
    mo_targets = defaultdict(set)
    for r in B.tsv(RAW / "zfin/Morpholinos.txt"):
        if len(r) > 3 and r[3].startswith("ZDB-MRPHLNO"):
            mo_targets[r[3]].add(r[0])
    comps = defaultdict(list)
    for r in B.tsv(RAW / "zfin/fish_components_fish.txt"):
        if len(r) > 5:
            comps[r[0]].append((r[2], r[4]))
    fish_gene, why = {}, Counter()
    for f, cs in comps.items():
        strs = {a for _, a in cs if a.startswith(B.STR_PREFIX)}
        if not strs:
            continue
        if len(strs) != 1:
            why["multiple_reagents"] += 1
            continue
        mo = next(iter(strs))
        if not mo.startswith("ZDB-MRPHLNO"):
            why["crispr_or_talen"] += 1
            continue
        if len(mo_targets.get(mo, ())) != 1:
            why["mo_multi_target_or_unknown"] += 1
            continue
        alts = {a for _, a in cs if a.startswith("ZDB-ALT")}
        if any(ftype.get(a, "") != "Transgenic Insertion" for a in alts):
            why["has_mutant_or_other_feature"] += 1
            continue
        genes = {g for g, a in cs if g}
        tgt = next(iter(mo_targets[mo]))
        if genes != {tgt}:
            why["other_gene_component"] += 1
            continue
        fish_gene[f] = tgt
        why["eligible_fish"] += 1
    return fish_gene, dict(why)


def task_a(ctx, emap, P):
    fish_gene, why = morphant_fish()
    fishes, out = zfin_records(fish_gene, emap)
    expr = B.load_expression()
    z_pm, z_mf = B.load_gaf(ROOT / "data/db_setup/go/zfin.gaf.gz")
    rows, feats = [], []
    for g in sorted(fishes):
        node = "ZFIN:" + g
        hs = ctx.alliance.get(node) or ctx.fb_zfin.get(node, set())
        anchor, cls, sub = ctx.best(hs)
        uid = "zfmo:" + g
        depth, fsz = ctx.covs(anchor)
        if not anchor:
            depth = len(z_pm.get(g, ()))
        ex = sorted(expr.get(node, ()))
        y, yx, leth, n = out[g]
        rows.append(dict(unit_id=uid, gene=g, species="zfmo", anchor=anchor, cls=cls, subclass=sub,
                         block=ctx.block(anchor, uid), src_mgi=0, src_impc=0, src_zfin=1, impc_center="none",
                         depth=depth, n_genotypes=len(fishes[g]), family_size=fsz, expr_breadth=len(ex),
                         Y=y, Y_exc=yx, lethal=leth, n_rec=n))
        mf = ctx.h_mf.get(anchor, set()) if anchor else z_mf.get(g, set())
        feats.append({"mf": sorted(mf), "expr": ex, "grp": sorted(ctx.fam.get(anchor, ())) if anchor else []})
    s = pd.DataFrame(rows)
    s["stratum"] = "zebrafish|morphant"
    res = {"eligibility_counts": why, "n_morphant_units": len(s),
           "unpaired_crude": crude(s, ["Y", "Y_exc"])}
    # T1-style: dbtest design + out-of-fold NN score (same k / shrink / folds rule), db_explore.t1_block
    E, enames = D.design(s)
    mats = {}
    for key in ("mf", "expr", "grp"):
        vocab, r_, c_ = {}, [], []
        for i, f in enumerate(feats):
            for t in set(f[key]):
                r_.append(i)
                c_.append(vocab.setdefault(t, len(vocab)))
        m = sparse.csr_matrix((np.ones(len(r_), np.float32), (r_, c_)), shape=(len(s), max(1, len(vocab))))
        m.data[:] = 1
        mats[key] = m
    folds = D.block_folds(s, P["n_folds"], P["seed"])
    nn = D.nn_index(s, mats, folds, P["k"])
    x = (s.cls == "class").astype(float).values
    cc = s.cls.isin(["class", "control"]).values
    rng = np.random.default_rng(13)
    res["t1"] = {"covariates": enames + ["nn_score"]}
    for col in ("Y", "Y_exc"):
        y = s[col].values.astype(float)
        nns = D.logit_safe(D.nn_score(nn, folds, y, s, P["nn_shrink"]))
        res["t1"][col] = X.t1_block(s, E, nns, x, y, cc, rng, N_BOOT, N_PERM)
    res["t1"]["n_class_blocks"] = int(s[s.cls == "class"].block.nunique())
    # paired with sealed mutant units
    su = pd.read_csv(ROOT / "data/db_setup/units_setup.csv", dtype=str, keep_default_na=False)
    ou = pd.read_csv(ROOT / "data/db_restricted/units_outcome.csv", dtype={"unit_id": str})
    mu = su[su.species == "zebrafish"].merge(ou, on="unit_id")
    mu["gene"] = mu.unit_id.str.replace("zebrafish:", "", regex=False)
    pr = mu[["gene", "cls", "Y", "Y_exc"]].merge(s[["gene", "cls", "Y", "Y_exc"]], on="gene",
                                                 suffixes=("_mut", "_mo"))
    res["paired"] = {"n_genes_both": len(pr), "cls_agree": int((pr.cls_mut == pr.cls_mo).sum()),
                     "class_from": "sealed mutant unit (units_setup.csv)"}
    for grp in ("class", "control", "grey", "other", "all"):
        q = pr if grp == "all" else pr[pr.cls_mut == grp]
        d = {"n_pairs": len(q)}
        for col in ("Y", "Y_exc"):
            a, b = q[col + "_mut"].astype(int), q[col + "_mo"].astype(int)
            n11, n10, n01, n00 = (int(((a == i) & (b == j)).sum()) for i, j in ((1, 1), (1, 0), (0, 1), (0, 0)))
            disc = n10 + n01
            p = binomtest(n01, disc, 0.5).pvalue if disc else 1.0
            d[col] = {"both1": n11, "mut1_mo0": n10, "mut0_mo1": n01, "both0": n00,
                      "rate_mut": round(a.mean(), 3) if len(q) else None,
                      "rate_mo": round(b.mean(), 3) if len(q) else None,
                      "concordance": round((n11 + n00) / len(q), 3) if len(q) else None,
                      "mcnemar_exact_p": float(f"{p:.3g}")}
        res["paired"][grp] = d
    # class-vs-control contrast of the morphant-minus-mutant discordance (descriptive)
    return res, s


# ---------------------------------------------------------------- Task B: species loaders

def load_xenopus(ctx):
    ch, nm, alt, repl, obs = parse_obo(ONT / "xpo.obo")
    words = [w for w in mouse_label_words() if w != "size"]
    Y, YX, YN, _ = term_sets("xenopus", ch, nm, words)
    recs, gp_of, taxa = defaultdict(list), defaultdict(set), defaultdict(set)
    unres = Counter()
    for r in B.tsv(RAW / "xenbase/GenePhenoRef.txt"):
        if len(r) < 10:
            continue
        gene, page, tax, term = r[0], r[2].replace("Xenbase:", ""), r[5], r[8]
        t = ROOTS["xenopus"]["obsolete_map"].get(term) or resolve(term, alt, repl, obs)
        if t is None:
            unres[term] += 1
            t = term
        recs[page].append(t)
        gp_of[page].add(gene)
        taxa[page].add(tax)
    fb = defaultdict(set)
    for r in B.tsv(RAW / "xenbase/XenbaseGeneHumanOrthologMapping.txt"):
        if len(r) > 1 and r[0].strip() in ctx.entrez:
            fb[r[1].strip()].add(ctx.entrez[r[0].strip()])
    units = []
    for page, ts in recs.items():
        hs = set().union(*(ctx.alliance.get(g, set()) for g in gp_of[page]))
        src = "alliance" if hs else ("xenbase_fallback" if fb.get(page) else "none")
        hs = hs or fb.get(page, set())
        units.append(dict(unit=page, records=ts, hs=hs, orth_src=src, taxa="|".join(sorted(taxa[page])),
                          morpholino_flag="unknown"))
    return units, (Y, YX, YN, {}), {"n_records": sum(len(u["records"]) for u in units),
                                     "obsolete_unresolved_records": sum(unres.values()),
                                     "obsolete_unresolved_terms": len(unres)}


def load_fly(ctx, broad=False):
    """broad=True (sensitivity): classical/insertion alleles with NO curated allele class are also accepted (most
    FlyBase classical alleles carry no class); any allele with a non-LOF class is still excluded."""
    ch, nm, alt, repl, obs = parse_obo(ONT / "fbbt-simple.obo", ("is_a", "part_of"))
    ch2, nm2, alt2, repl2, obs2 = parse_obo(ONT / "fbcv.obo")
    for k, v in ch2.items():
        ch[k] |= v
    nm.update(nm2)
    alt.update(alt2)
    repl.update(repl2)
    obs |= obs2
    words = [w for w in mouse_label_words() if w != "size"]
    Y, YX, YN, extra = term_sets("fly", ch, nm, words)
    allele = {}
    for r in B.tsv(RAW / "flybase/dmel_classical_and_insertion_allele_descriptions_fb_2026_03.tsv.gz"):
        if len(r) < 14 or not r[1].startswith("FBal"):
            continue
        cl = r[4].lower()
        lof = bool(re.search(r"amorphic|hypomorphic|loss of function", cl)) and not re.search(
            r"antimorphic|neomorphic|hypermorphic|gain of function|wild-type", cl)
        if broad and not cl.strip():
            lof = True
        allele[r[1]] = (r[3], lof and not r[12].strip())
    recs = defaultdict(list)
    why = Counter()
    for r in B.tsv(RAW / "flybase/genotype_phenotype_data_fb_2026_03.tsv.gz"):
        if len(r) < 4:
            continue
        ids = [i for i in re.split(r"[ /]+", r[1].strip()) if i]
        if not ids or any(not i.startswith("FBal") for i in ids):
            why["non_allele_component"] += 1
            continue
        info = [allele.get(i) for i in ids]
        if any(x is None for x in info):
            why["allele_not_classical_insertion"] += 1
            continue
        genes = {g for g, _ in info}
        if len(genes) != 1:
            why["multi_gene"] += 1
            continue
        if not all(ok for _, ok in info):
            why["not_lof_class"] += 1
            continue
        t = resolve(r[3], alt, repl, obs) or r[3]
        recs[next(iter(genes))].append(t)
        why["eligible_records"] += 1
    fb = defaultdict(set)
    for r in B.tsv(RAW / "flybase/dmel_human_orthologs_disease_fb_2026_03.tsv.gz"):
        if len(r) > 2 and r[2].startswith("HGNC:"):
            fb[r[0]].add(r[2])
    units = []
    for g, ts in recs.items():
        hs = ctx.alliance.get("FB:" + g, set())
        src = "alliance" if hs else ("flybase_fallback" if fb.get(g) else "none")
        units.append(dict(unit=g, records=ts, hs=hs or fb.get(g, set()), orth_src=src))
    return units, (Y, YX, YN, extra), dict(why)


def load_human(ctx):
    ch, nm, alt, repl, obs = parse_obo(RAW / "hpo/hp.obo")
    Y, YX, YN, _ = term_sets("human", ch, nm, mouse_label_words())
    recs = defaultdict(list)
    miss = 0
    with open(RAW / "hpo/genes_to_phenotype.txt", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            h = ctx.entrez.get(r["ncbi_gene_id"].strip())
            if not h:
                miss += 1
                continue
            recs[h].append(resolve(r["hpo_id"], alt, repl, obs) or r["hpo_id"])
    units = [dict(unit=h, records=ts, hs={h}, orth_src="self") for h, ts in recs.items()]
    return units, (Y, YX, YN, {}), {"rows_without_hgnc": miss}


def build_species(ctx, sp, loader, upm, mY, mX):
    units, (Y, YX, YN, extra), info = loader(ctx)
    rows = []
    for u in units:
        anchor, cls, sub = ctx.best(u["hs"])
        uid = f"{sp}:{u['unit']}"
        depth, fsz = ctx.covs(anchor)
        ts = u["records"]
        mp = [upm.get(t, set()) for t in ts]
        row = dict(unit_id=uid, anchor=anchor, cls=cls, subclass=sub, block=ctx.block(anchor, uid), depth=depth,
                   family_size=fsz, orth_src=u["orth_src"], n_rec=len(ts),
                   Y=int(any(t in Y for t in ts)), Y_exc=int(any(t in YX for t in ts)),
                   Y_nosize=int(any(t in YN for t in ts)),
                   Y_upheno=int(any(m & mY for m in mp)), Y_exc_upheno=int(any(m & mX for m in mp)),
                   rec_upheno_mapped=sum(1 for m in mp if m))
        for k, S in extra.items():
            row[k] = int(any(t in S for t in ts))
        rows.append(row)
    df = pd.DataFrame(rows)
    info.update({"n_Y_terms": len(Y), "n_Yexc_terms": len(YX), "n_Ynosize_terms": len(YN),
                 "orth_src": dict(Counter(df.orth_src)),
                 "upheno_record_coverage": round(df.rec_upheno_mapped.sum() / max(1, df.n_rec.sum()), 3)})
    return df, info


# ---------------------------------------------------------------- report

def fmt_or(d):
    if not d or d.get("or") is None:
        return "n/a"
    return f"{d['or']} [{d['lo']}, {d['hi']}] p1={d['perm_p_one_sided']}"


def write_md(out, path):
    L = ["# Secondary species and zebrafish morphant analyses (EXPLORATORY)", "",
         "Prereg plans/pivot_db_v1.md section J (queue Q012, Q013). **Exploratory: cannot change the sealed verdict** "
         "(reports/db_counted_v1.json: FAIL; adjusted OR 0.78 class vs control; positive control Y_exc OR 1.89).", "",
         "Code: harness/db_secondary.py (method choices in its docstring and ROOTS dict). Numbers: "
         "reports/db_secondary_v1.json.", "", "## Task B: secondary species", "",
         "Adjusted OR = class (channel/pump) vs control (matched membrane genes), logistic regression with "
         "z(log1p GO-PMID depth of the human anchor) and z(log1p HGNC family size); 95% block-bootstrap CI (1000); "
         "one-sided block-permutation p (1000).", "",
         "| species | n class / control (class blocks) | Y rate class / control | adj OR Y | Y_exc rate class / control "
         "| adj OR Y_exc (positive control) |", "|---|---|---|---|---|---|"]
    for sp in ("xenopus", "fly", "fly_broad", "human"):
        r = out["species"][sp]
        c = r["crude"]
        L.append(f"| {sp} | {r['n_class']} / {r['n_control']} ({r['n_class_blocks']}) | "
                 f"{c['class']['Y_rate']} / {c['control']['Y_rate']} | {fmt_or(r['adjusted']['Y'])} | "
                 f"{c['class']['Y_exc_rate']} / {c['control']['Y_exc_rate']} | {fmt_or(r['adjusted']['Y_exc'])} |")
    L += ["", "Endpoint variants (adjusted OR, class vs control):", "",
          "| species | Y_nosize | Y_upheno (uPheno->mouse Y set) | Y_exc_upheno | other | uPheno record coverage |",
          "|---|---|---|---|---|---|"]
    for sp in ("xenopus", "fly", "fly_broad", "human"):
        r = out["species"][sp]
        a = r["adjusted"]
        oth = "; ".join(f"{k}: {fmt_or(v)}" for k, v in a.items() if k not in
                        ("Y", "Y_exc", "Y_nosize", "Y_upheno", "Y_exc_upheno")) or "-"
        L.append(f"| {sp} | {fmt_or(a.get('Y_nosize'))} | {fmt_or(a.get('Y_upheno'))} | "
                 f"{fmt_or(a.get('Y_exc_upheno'))} | {oth} | {r['info']['upheno_record_coverage']} |")
    L += ["", "Crude rates by class (n, Y rate, Y_exc rate):", ""]
    for sp in ("xenopus", "fly", "fly_broad", "human"):
        c = out["species"][sp]["crude"]
        L.append(f"- {sp}: " + "; ".join(f"{k} n={c[k]['n']} Y={c[k]['Y_rate']} Yexc={c[k]['Y_exc_rate']}"
                                         for k in ("class", "control", "grey", "other"))
                 + f"; median annotation records per unit (descriptive only, not a covariate) "
                   f"{out['species'][sp]['median_n_records']}")
    A = out["morphant"]
    L += ["", "## Task A: zebrafish morphants vs mutants", "",
          f"Morphant units: {A['n_morphant_units']} (eligible single-MO fish: "
          f"{A['eligibility_counts'].get('eligible_fish')}). Genes with both a mutant and a morphant unit: "
          f"{A['paired']['n_genes_both']}.", "",
          "| group | pairs | Y mut / MO rate | Y both1, mut-only, MO-only, both0 | McNemar p | Y_exc mut / MO rate "
          "| Y_exc both1, mut-only, MO-only, both0 | McNemar p |", "|---|---|---|---|---|---|---|---|"]
    for g in ("class", "control", "other", "grey", "all"):
        d = A["paired"][g]
        y, e = d["Y"], d["Y_exc"]
        L.append(f"| {g} | {d['n_pairs']} | {y['rate_mut']} / {y['rate_mo']} | {y['both1']}, {y['mut1_mo0']}, "
                 f"{y['mut0_mo1']}, {y['both0']} | {y['mcnemar_exact_p']} | {e['rate_mut']} / {e['rate_mo']} | "
                 f"{e['both1']}, {e['mut1_mo0']}, {e['mut0_mo1']}, {e['both0']} | {e['mcnemar_exact_p']} |")
    c = A["unpaired_crude"]
    L += ["", "Unpaired morphant rates: " + "; ".join(
        f"{k} n={c[k]['n']} Y={c[k]['Y_rate']} Yexc={c[k]['Y_exc_rate']}" for k in ("class", "control", "grey", "other")),
          "", f"T1-style adjusted OR on morphant units (dbtest design: depth, n_genotypes, family size, expression "
              f"breadth + out-of-fold NN score; block bootstrap / permutation 1000): Y {fmt_or(A['t1']['Y'])}; "
              f"Y_exc {fmt_or(A['t1']['Y_exc'])}; class blocks {A['t1']['n_class_blocks']}.", "",
          "## Method choices", ""]
    L += [f"- {x}" for x in out["method_choices"]]
    L += ["", "## Caveats", ""] + [f"- {x}" for x in out["caveats"]]
    Path(path).write_text("\n".join(L) + "\n")


def main():
    P = json.loads((ROOT / "config/db_params_v1.json").read_text())
    emap = json.loads((ROOT / "config/db_endpoint_map_v1.json").read_text())
    mY, mX = set(emap["mouse"]["Y_terms"]), set(emap["mouse"]["Y_exc_terms"])
    ctx = Ctx()
    ctx.fb_zfin = {}
    for r in B.tsv(RAW / "zfin/human_orthos.txt"):
        if len(r) > 7 and r[7].strip().isdigit():
            ctx.fb_zfin.setdefault("ZFIN:" + r[0], set()).add("HGNC:" + r[7].strip())
    upm = upheno_map()
    out = {"note": "EXPLORATORY (prereg plans/pivot_db_v1.md section J; queue Q012/Q013). Cannot change the sealed "
                   "verdict in reports/db_counted_v1.json.", "species": {}}
    seeds = {"xenopus": 21, "fly": 22, "human": 23}
    seeds["fly_broad"] = 24
    loaders = {"xenopus": load_xenopus, "fly": load_fly, "fly_broad": lambda c: load_fly(c, True),
               "human": load_human}
    for sp, ld in loaders.items():
        df, info = build_species(ctx, sp.split("_")[0], ld, upm, mY, mX)
        ycols = ["Y", "Y_exc", "Y_nosize", "Y_upheno", "Y_exc_upheno"] + (["Y_eye"] if sp.startswith("fly") else [])
        res = species_analysis(df, ycols, seeds[sp])
        res["info"] = info
        out["species"][sp] = res
        print(sp, res["n_class"], res["n_control"], res["adjusted"]["Y"], res["adjusted"]["Y_exc"], flush=True)
    res, _ = task_a(ctx, emap, P)
    out["morphant"] = res
    print("morphant", json.dumps(res["paired"]["class"]), res["t1"]["Y"], flush=True)
    out["roots"] = ROOTS
    out["method_choices"] = [
        "Human (HPO genes_to_phenotype): unit = HGNC gene (anchor = itself); include roots axial skeleton, rib, "
        "sternum, girdles, sacrum, head (HP:0000234), limbs (HP:0040064), appendicular skeleton, heterotaxy/situs/"
        "dextrocardia/L-looping, neural tube defect; excluded areas nervous system, cardiovascular, musculature, eye, "
        "ear, integument, metabolism/homeostasis, growth, mortality, endocrine (laterality and neural-tube terms kept), "
        "plus spine curvature, enamel, dental colour, dental eruption, tongue, oral mucosa (mirroring the mouse extra "
        "exclusions); mouse label-word list applied verbatim.",
        "Xenopus (XPO): entity roots for axial skeleton, left-right axis/organizer, somite, AP/DV/main body axes, "
        "ventralized/dorsalized embryo, blastopore, neural tube/fold, notochord, cranial neural crest, craniofacial "
        "region/skeleton, head, pharyngeal arch, tail region/bud, limb/limb bud, fin, girdles, paraxial and axial "
        "mesoderm; XPO process terms (flat under XPO:0116434) included by a label pattern (axis, left/right, "
        "gastrulation, somite, segmentation, convergent extension, neural tube/crest/fold, notochord, heart looping, "
        "blastopore, pattern specification ...); excluded nervous system, cardiovascular, heart, muscle, eye/visual "
        "system, inner ear/otic, lateral line, pigment cells, behaviour, death; label words = mouse list without "
        "'size'. Obsolete XPO ids resolved through replaced_by where present; two obsolete axis-duplication ids without "
        "replaced_by (XPO:0115824, XPO:0115825) hand-mapped to 'duplicated main body axis' (XPO:0141924); the rest "
        "left unmatched (counted in info).",
        "fly_broad (sensitivity): also accepts classical/insertion alleles with no curated allele class (about 90% "
        "of classical alleles have none), still excluding any non-LOF class, aberrations, transgenic constructs "
        "(UAS/GAL4/RNAi are not in the classical allele file) and alleles carrying an encoded product.",
        "Fly: Y = FBcv segmentation (gap/pair-rule/segment polarity), axis specification, DV axis, planar polarity, "
        "homeotic; FBbt (is_a + part_of) wing, wing disc, leg, leg disc, haltere, haltere disc, eye-antennal disc, "
        "embryonic segment, embryonic/first-instar cuticle; minus nervous system, neuron, glia, muscle cell, somatic "
        "muscle, dorsal vessel and the adult eye (variant Y_eye keeps the adult eye/ommatidia). FlyBase FBbt "
        "annotations carry no quality, so wing size and wing pattern defects cannot be separated (Y_nosize is "
        "therefore near-identical to Y for fly).",
        "uPheno variant: species term counts when it has a uPheno crossSpeciesExactMatch (direct or via a shared "
        "UPHENO class) to an MP term in the sealed mouse Y set; this is the most faithful cross-species translation "
        "but covers only terms with an MP equivalent (coverage reported per species).",
        "Y_nosize: drops terms whose label contains small/short/long/large/enlarged/elongated/size/length/width/height/"
        "macro/micro/hypoplas/hyperplas/aplasia/decreased/increased/thin/thick (stricter than the mouse nosize rule).",
        "Morphants: see docstring; Y/Y_exc via a verbatim copy of the sealed ZFIN record loop.",
    ]
    out["caveats"] = [
        "Exploratory, many endpoint choices made after the sealed result was known; treat as hypothesis generating.",
        "Xenopus GenePhenoRef has no reagent column: morpholino, mutant, CRISPR F0 and mRNA overexpression records "
        "are pooled (morpholino flag = unknown for all). Overexpression of a channel can create gain-of-function "
        "phenotypes, so Xenopus is not a loss-of-function test.",
        "Human HPO annotations are disease-gene level and ascertainment-driven: channel genes enter mostly through "
        "channelopathies (epilepsy, arrhythmia, myopathy), and gene-level phenotype annotation counts are large for "
        "syndromic genes; the depth covariate only partly adjusts. Variant mechanism (LOF vs GOF) is not filtered. "
        "Class genes carry about twice as many HPO annotations as control genes (median_n_records), and Y is "
        "'any annotation in the set', so the human OR is expected to be inflated by annotation density (the "
        "forbidden covariate); the head root also captures facial dysmorphism common in channelopathy-related "
        "neurodevelopmental syndromes.",
        "Fly endpoint is anatomy-only (no quality), so 'wing' includes size, vein and margin defects; bristle "
        "patterning on the notum is not in Y. Fly class membership depends on the human anchor; many fly channel "
        "families map one-to-many to human genes.",
        "No NN score for secondary species (no expression/MF features built for them); covariates restricted to depth "
        "and family size as specified.",
        "Morphant phenotypes are known to include off-target/toxicity artefacts (p53-mediated apoptosis, necrosis, "
        "edema); the paired McNemar compares annotation-level outcomes from different publications, not matched "
        "experiments.",
    ]
    (ROOT / "reports/db_secondary_v1.json").write_text(json.dumps(out, indent=1, default=lambda o: sorted(o)
                                                                  if isinstance(o, set) else str(o)))
    write_md(out, ROOT / "reports/db_secondary_v1.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

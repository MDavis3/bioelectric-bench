"""FAERS drug-exposure probe v1 (sealed plan: plans/faers_probe_v1.md).

Exploratory probe, not a verdict. Fetches openFDA drug/event counts (meta.results.total) for
class (ion channel/pump primary target) vs indication-matched comparator drugs in 6 strata, then
computes per-stratum reporting odds ratios (Woolf CI) and Mantel-Haenszel pooled ROR (RBG CI)
for outcome A (seriousnesscongenitalanomali=1) and outcome B (core-malformation MedDRA PTs).

Usage: python3 harness/faers_probe.py [--fetch]   (without --fetch, re-analyses cached raw JSON)
"""
import argparse
import hashlib
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_db" / "faers"
MANIFEST = ROOT / "data" / "raw_db_manifest_faers.json"
OUT_JSON = ROOT / "reports" / "faers_probe_v1.json"
BASE = "https://api.fda.gov/drug/event.json"
UA = "bioelectric-bench-fetch/1.0 (research)"
SLEEP = 0.6  # ~100 req/min max, well under 240/min

# Sealed strata (do not edit).
STRATA = [
    ("Epilepsy", ["CARBAMAZEPINE", "OXCARBAZEPINE", "PHENYTOIN", "LAMOTRIGINE", "LACOSAMIDE", "ETHOSUXIMIDE"],
     ["LEVETIRACETAM"]),
    ("Acid suppression", ["OMEPRAZOLE", "ESOMEPRAZOLE", "LANSOPRAZOLE", "PANTOPRAZOLE"],
     ["FAMOTIDINE", "RANITIDINE", "CIMETIDINE"]),
    ("Nausea", ["ONDANSETRON", "GRANISETRON"], ["METOCLOPRAMIDE", "PROMETHAZINE", "DOXYLAMINE"]),
    ("Type 2 diabetes", ["GLYBURIDE", "GLIPIZIDE", "GLIMEPIRIDE"], ["METFORMIN"]),
    ("Hypertension", ["NIFEDIPINE", "AMLODIPINE", "VERAPAMIL", "DILTIAZEM"], ["LABETALOL", "METHYLDOPA", "HYDRALAZINE"]),
    ("Neuropathic pain", ["GABAPENTIN", "PREGABALIN"], ["DULOXETINE"]),
]

# Outcome B PTs: plan list, openFDA exact spellings (verified by total>0 on reactionmeddrapt.exact).
# "Vertebral anomaly" has no PT in openFDA; nearest PT used is SPINE MALFORMATION (flagged; B_strict omits it).
PT_STRICT = ["CLEFT LIP", "CLEFT PALATE", "CLEFT LIP AND PALATE", "POLYDACTYLY", "SYNDACTYLY",
             "LIMB REDUCTION DEFECT", "ECTRODACTYLY", "NEURAL TUBE DEFECT", "SPINA BIFIDA", "ANENCEPHALY",
             "CRANIOSYNOSTOSIS", "SITUS INVERSUS", "HETEROTAXIA", "DEXTROCARDIA", "HEMIVERTEBRA"]
PT_B = PT_STRICT + ["SPINE MALFORMATION"]


def drug_clause(drugs):
    if len(drugs) == 1:
        return f'patient.drug.openfda.generic_name:"{drugs[0]}"'
    return "patient.drug.openfda.generic_name:(" + "+".join(f'"{d}"' for d in drugs) + ")"


def pt_clause(pts):
    return "patient.reaction.reactionmeddrapt.exact:(" + "+".join(f'"{p}"' for p in pts) + ")"


OUTCOMES = {
    "total": None,
    "A": "seriousnesscongenitalanomali:1",
    "B": pt_clause(PT_B),
    "B_strict": pt_clause(PT_STRICT),
}


def build_url(search):
    # openFDA uses '+' as space; keep quotes/parens/colons literal-ish but escape spaces and quotes.
    q = urllib.parse.quote(search, safe='+:()"*.')
    return f"{BASE}?search={q}&limit=1"


def fname(key):
    return key.replace(" ", "_").replace("/", "_") + ".json"


_manifest = []


def fetch(key, search, do_fetch):
    path = RAW / fname(key)
    url = build_url(search)
    if do_fetch:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    body = r.read()
                break
            except urllib.error.HTTPError as e:
                body = e.read()
                if e.code == 404:
                    break
                if e.code == 429 or e.code >= 500:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise SystemExit(f"HTTP {e.code} for {url}: {body[:300]}")
        path.write_bytes(body)
        _manifest.append({"key": key, "url": url, "local_path": str(path.relative_to(ROOT)),
                          "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                          "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        time.sleep(SLEEP)
    d = json.loads(path.read_text())
    if "error" in d:
        if d["error"].get("code") == "NOT_FOUND":
            return 0
        raise SystemExit(f"API error for {key}: {d['error']}")
    return int(d["meta"]["results"]["total"])


def ror(a, b, c, d):
    """a=class w/ outcome, b=class w/o, c=comp w/ outcome, d=comp w/o. Woolf CI, +0.5 if any zero."""
    cc = any(x == 0 for x in (a, b, c, d))
    if cc:
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    r = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return {"ror": r, "lo": math.exp(math.log(r) - 1.96 * se), "hi": math.exp(math.log(r) + 1.96 * se),
            "continuity_corrected": cc}


def mh_rbg(tables):
    """Mantel-Haenszel OR with Robins-Breslow-Greenland variance. tables: list of (a,b,c,d)."""
    R = S = PR = PS_QR = QS = 0.0
    for a, b, c, d in tables:
        n = a + b + c + d
        if n == 0:
            continue
        Ri, Si = a * d / n, b * c / n
        Pi, Qi = (a + d) / n, (b + c) / n
        R += Ri; S += Si
        PR += Pi * Ri; PS_QR += Pi * Si + Qi * Ri; QS += Qi * Si
    orr = R / S
    var = PR / (2 * R ** 2) + PS_QR / (2 * R * S) + QS / (2 * S ** 2)
    se = math.sqrt(var)
    return {"ror": orr, "lo": math.exp(math.log(orr) - 1.96 * se), "hi": math.exp(math.log(orr) + 1.96 * se),
            "se_log": se}


def reading(p):
    if p["ror"] > 1.5 and p["lo"] > 1:
        return "signal worth a proper pregnancy-cohort test"
    if p["lo"] <= 1 <= p["hi"]:
        return "no signal in reporting data"
    return "outside pre-stated categories (interval excludes 1 but ROR <= 1.5, or ROR < 1 with interval below 1)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)

    counts = {}
    strata_out = []
    for name, cls, comp in STRATA:
        s = {"stratum": name, "class": cls, "comparator": comp, "group": {}, "per_drug": {}}
        for arm, drugs in (("class", cls), ("comparator", comp)):
            g = {}
            for o, extra in OUTCOMES.items():
                search = drug_clause(drugs) + (f"+AND+{extra}" if extra else "")
                g[o] = fetch(f"group__{name}__{arm}__{o}", search, args.fetch)
            s["group"][arm] = g
            for dname in drugs:
                pd = {}
                for o in ("total", "A", "B"):
                    extra = OUTCOMES[o]
                    search = drug_clause([dname]) + (f"+AND+{extra}" if extra else "")
                    pd[o] = fetch(f"drug__{dname}__{o}", search, args.fetch)
                s["per_drug"][dname] = pd
        # overlap: reports listing both a class and a comparator drug
        s["overlap_total"] = fetch(f"overlap__{name}__total",
                                   drug_clause(cls) + "+AND+" + drug_clause(comp), args.fetch)
        # summed per-drug (double counts multi-drug reports within a group)
        s["summed"] = {arm: {o: sum(s["per_drug"][d][o] for d in drugs) for o in ("total", "A", "B")}
                       for arm, drugs in (("class", cls), ("comparator", comp))}
        s["ror"] = {}
        for basis in ("group", "summed"):
            src = s[basis]
            for o in (("A", "B", "B_strict") if basis == "group" else ("A", "B")):
                a, N1 = src["class"][o], src["class"]["total"]
                c, N0 = src["comparator"][o], src["comparator"]["total"]
                s["ror"][f"{basis}_{o}"] = {"table": [a, N1 - a, c, N0 - c], **ror(a, N1 - a, c, N0 - c)}
        strata_out.append(s)

    pooled = {}
    for key in ("group_A", "group_B", "group_B_strict", "summed_A", "summed_B"):
        tabs = [tuple(s["ror"][key]["table"]) for s in strata_out]
        p = mh_rbg(tabs)
        p["reading_if_outcome_B"] = reading(p) if "B" in key else None
        pooled[key] = p

    out = {
        "probe": "faers_probe_v1", "plan": "plans/faers_probe_v1.md", "source": BASE,
        "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "primary_basis": "group-level OR queries (each report counted once per arm)",
        "outcome_A": OUTCOMES["A"], "outcome_B_PTs": PT_B, "outcome_B_strict_PTs": PT_STRICT,
        "pt_notes": "Plan PT 'vertebral anomaly' has no openFDA PT; mapped to SPINE MALFORMATION (B). "
                    "B_strict = plan PTs with exact matches only.",
        "strata": strata_out, "pooled_MH": pooled,
        "prestated_reading_primary_B": pooled["group_B"]["reading_if_outcome_B"],
    }
    OUT_JSON.write_text(json.dumps(out, indent=1))
    if args.fetch:
        MANIFEST.write_text(json.dumps(_manifest, indent=1))
    for k, p in pooled.items():
        print(f"{k}: MH ROR {p['ror']:.3f} ({p['lo']:.3f}-{p['hi']:.3f})")
    for s in strata_out:
        r = s["ror"]
        print(f"{s['stratum']:18s} A {r['group_A']['ror']:.2f} ({r['group_A']['lo']:.2f}-{r['group_A']['hi']:.2f})"
              f"  B {r['group_B']['ror']:.2f} ({r['group_B']['lo']:.2f}-{r['group_B']['hi']:.2f}) tab={r['group_B']['table']}")


if __name__ == "__main__":
    sys.exit(main())

"""Write data/raw_db_manifest.json from the fetch list + fetch log. Hashes/sizes only; never reads content
beyond hashing. Run with python3 -I."""
import hashlib, json, os, sys

files_lst, log_path, out = sys.argv[1:4]
fetched = {}
with open(log_path) as fh:
    for line in fh:
        ts, rc, path, url = line.rstrip("\n").split("\t")
        fetched[path] = (ts, rc)

ROBOTS_OK = True  # every fetched host checked 2026-11-10; disallowed hosts (ftp.ebi.ac.uk) are not in the list
rows = []
with open(files_lst) as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        dest, url, lic = line.split("|", 2)
        path = os.path.join(dest, os.path.basename(url))
        row = {"source": os.path.basename(dest), "url": url, "local_path": path,
               "bytes": None, "sha256": None, "fetched_utc": fetched.get(path, (None,))[0],
               "license": lic, "robots_ok": ROBOTS_OK}
        if os.path.isfile(path):
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            row["bytes"] = os.path.getsize(path)
            row["sha256"] = h.hexdigest()
        rows.append(row)

skipped = [
    {"source": "impc", "url": "https://ftp.ebi.ac.uk/pub/databases/impc/all-data-releases/latest/results/",
     "local_path": None, "bytes": None, "sha256": None, "fetched_utc": None, "license": "CC-BY-4.0",
     "robots_ok": False, "note": "ftp.ebi.ac.uk robots.txt: User-agent * Disallow / ; not fetched"},
    {"source": "alliance", "url": "https://fms.alliancegenome.org/download/PHENOTYPE-ALLIANCE_COMBINED.tsv.gz",
     "local_path": None, "bytes": None, "sha256": None, "fetched_utc": None, "license": "CC-BY-4.0",
     "robots_ok": True, "note": "FMS returns HTTP 500; no PHENOTYPE-ALLIANCE datafile registered; not fetched"},
]
with open(out, "w") as fh:
    json.dump(rows + skipped, fh, indent=1)
print(f"manifest rows: {len(rows)} fetched-list, {len(skipped)} skipped -> {out}")

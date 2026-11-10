#!/usr/bin/env bash
# Reproducible fetch of public gene-perturbation phenotype databases + predictor-side gene-class sources.
# Outcome-bearing dumps -> data/raw_db/<source>/ (git-ignored; FIREWALL: planner must not read contents).
# Predictor-side files -> data/db_setup/<source>/ (planner-readable).
# Usage:  bash harness/fetch_db.sh            # download (resumable), verify, write manifest
#         bash harness/fetch_db.sh --verify   # only re-hash and compare to data/raw_db_SHA256SUMS
# robots.txt of every host was checked on 2026-11-10 (see ROBOTS notes below). Nothing downloaded is executed.
set -uo pipefail
cd "$(dirname "$0")/.."
UA="bioelectric-bench-fetch/1.0 (research)"
SUMS=data/raw_db_SHA256SUMS
LOG=data/raw_db/_fetch_log.tsv
mkdir -p data/raw_db data/db_setup

# ROBOTS (2026-11-10):
#  data.monarchinitiative.org, download.xenbase.org, s3ftp.flybase.org, storage.googleapis.com, www.genenames.org,
#  www.informatics.jax.org, www.guidetopharmacology.org, fms.alliancegenome.org: no robots.txt (404/HTML) -> allowed
#  www.alliancegenome.org: Allow / (except /search,/alliancemine,/jbrowse); zfin.org: /downloads allowed, Crawl-delay 1
#  current.geneontology.org: Allow /; github.com: /releases/download allowed; purl.obolibrary.org -> github release assets
#  ftp.ebi.ac.uk: "User-agent: * Disallow: /"  -> IMPC NOT fetched (obeying robots)
#  ftp.flybase.net: connection refused -> used s3ftp.flybase.org mirror
#  Alliance PHENOTYPE-ALLIANCE_* files: FMS returns HTTP 500 / no datafile registered -> not fetched

# dest_dir | url | license
read -r -d '' FILES <<'EOF'
data/raw_db/monarch|https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.tar.gz|CC-BY-4.0 (Monarch KG; component source licenses in metadata.yaml)
data/raw_db/monarch|https://data.monarchinitiative.org/monarch-kg/latest/metadata.yaml|CC-BY-4.0
data/raw_db/monarch|https://data.monarchinitiative.org/mappings/latest/upheno-cross-species.sssom.tsv|CC-BY-4.0
data/raw_db/monarch|https://data.monarchinitiative.org/mappings/latest/upheno-species-independent.sssom.tsv|CC-BY-4.0
data/raw_db/alliance|https://fms.alliancegenome.org/download/ORTHOLOGY-ALLIANCE_COMBINED.tsv.gz|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/phenoGeneCleanData_fish.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/phenotype_fish.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/pheno_environment_fish.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/fish_model_disease.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/fish_components_fish.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/genotype_features.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/features.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/Morpholinos.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/CRISPR.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/TALEN.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/human_orthos.txt|CC-BY-4.0
data/raw_db/zfin|https://zfin.org/downloads/gene.txt|CC-BY-4.0
data/raw_db/xenbase|https://download.xenbase.org/xenbase/GenePageReports/GenePhenoRef.txt|CC-BY-4.0
data/raw_db/xenbase|https://download.xenbase.org/xenbase/GenePageReports/XenbaseGeneHumanOrthologMapping.txt|CC-BY-4.0
data/raw_db/xenbase|https://download.xenbase.org/xenbase/GenePageReports/GenePageGeneralInfo_ManuallyCurated.txt|CC-BY-4.0
data/raw_db/mgi|https://www.informatics.jax.org/downloads/reports/MGI_GenePheno.rpt|CC-BY-4.0
data/raw_db/mgi|https://www.informatics.jax.org/downloads/reports/MGI_PhenoGenoMP.rpt|CC-BY-4.0
data/raw_db/mgi|https://www.informatics.jax.org/downloads/reports/MGI_PhenotypicAllele.rpt|CC-BY-4.0
data/raw_db/mgi|https://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt|CC-BY-4.0
data/raw_db/mgi|https://www.informatics.jax.org/downloads/reports/HMD_HumanPhenotype.rpt|CC-BY-4.0
data/raw_db/mgi|https://www.informatics.jax.org/downloads/reports/MRK_List2.rpt.gz|CC-BY-4.0
data/raw_db/mgi|https://www.informatics.jax.org/downloads/reports/VOC_MammalianPhenotype.rpt|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/alleles/genotype_phenotype_data_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/alleles/dmel_classical_and_insertion_allele_descriptions_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/genes/gene_group_data_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/genes/gene_groups_HGNC_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/genes/fbgn_fbtr_fbpp_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/genes/fbgn_annotation_ID_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/orthologs/dmel_human_orthologs_disease_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/synonyms/fb_synonym_fb_2026_03.tsv.gz|CC-BY-4.0
data/raw_db/flybase|https://s3ftp.flybase.org/releases/current/precomputed_files/md5sum.txt|CC-BY-4.0
data/raw_db/hpo|https://purl.obolibrary.org/obo/hp/hpoa/genes_to_phenotype.txt|HPO license (free with attribution; hpo.jax.org/license)
data/raw_db/hpo|https://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa|HPO license (free with attribution; hpo.jax.org/license)
data/raw_db/hpo|https://purl.obolibrary.org/obo/hp.obo|HPO license (free with attribution; hpo.jax.org/license)
data/raw_db/ontologies|https://purl.obolibrary.org/obo/uberon/uberon-basic.obo|CC-BY-3.0
data/raw_db/ontologies|https://purl.obolibrary.org/obo/mp.obo|CC-BY-4.0
data/raw_db/ontologies|https://purl.obolibrary.org/obo/zp.obo|CC-BY-3.0
data/raw_db/ontologies|https://purl.obolibrary.org/obo/xpo.obo|CC-BY-4.0
data/raw_db/ontologies|https://purl.obolibrary.org/obo/fbcv.obo|CC-BY-4.0
data/raw_db/ontologies|https://purl.obolibrary.org/obo/fbbt/fbbt-simple.obo|CC-BY-4.0
data/raw_db/ontologies|https://purl.obolibrary.org/obo/go/go-basic.obo|CC-BY-4.0
data/raw_db/ontologies|https://github.com/obophenotype/upheno-dev/releases/download/v2025-07-21/upheno-base-with-bridge.obo|CC-BY-4.0
data/db_setup/hgnc|https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt|CC0-1.0
data/db_setup/hgnc|https://storage.googleapis.com/public-download-files/hgnc/csv/csv/genefamily_db_tables/family.csv|CC0-1.0
data/db_setup/hgnc|https://storage.googleapis.com/public-download-files/hgnc/csv/csv/genefamily_db_tables/hierarchy.csv|CC0-1.0
data/db_setup/hgnc|https://storage.googleapis.com/public-download-files/hgnc/csv/csv/genefamily_db_tables/hierarchy_closure.csv|CC0-1.0
data/db_setup/hgnc|https://storage.googleapis.com/public-download-files/hgnc/csv/csv/genefamily_db_tables/gene_has_family.csv|CC0-1.0
data/db_setup/iuphar|https://www.guidetopharmacology.org/DATA/targets_and_families.csv|CC-BY-SA-4.0
data/db_setup/iuphar|https://www.guidetopharmacology.org/DATA/GtP_to_HGNC_mapping.csv|CC-BY-SA-4.0
data/db_setup/go|https://current.geneontology.org/annotations/goa_human.gaf.gz|CC-BY-4.0
data/db_setup/go|https://current.geneontology.org/annotations/mgi.gaf.gz|CC-BY-4.0
data/db_setup/go|https://current.geneontology.org/annotations/zfin.gaf.gz|CC-BY-4.0
data/db_setup/go|https://current.geneontology.org/annotations/fb.gaf.gz|CC-BY-4.0
data/db_setup/go|https://current.geneontology.org/annotations/xenbase.gaf.gz|CC-BY-4.0
EOF

fetch_one() {  # dest url
  local dest="$1" url="$2" f; f="$dest/$(basename "$url")"
  mkdir -p "$dest"
  local remote rc
  remote=$(curl -sIL -A "$UA" "$url" | awk 'BEGIN{IGNORECASE=1} /^content-length/{l=$2} END{gsub("\r","",l); print l}')
  if [[ -s "$f" && -n "$remote" && "$(wc -c <"$f" | tr -d ' ')" == "$remote" ]]; then
    rc=0  # already complete
  else
    # HTTP/1.1: jax.org HTTP/2 streams dropped mid-file (curl 92) on 2026-11-10; -C - resumes partials
    curl -sSL --fail --http1.1 -A "$UA" --retry 5 --retry-delay 5 --retry-all-errors -C - -o "$f" "$url" 2>>"$dest/_curl_err.txt"
    rc=$?
    if [[ -n "$remote" && "$(wc -c <"$f" | tr -d ' ')" != "$remote" ]]; then rc=99; fi  # size mismatch
  fi
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" "$f" "$url" >> "$LOG"
}

if [[ "${1:-}" != "--verify" ]]; then
  : > "$LOG"
  # one serial worker per host (zfin.org needs Crawl-delay 1); hosts run in parallel
  hosts=$(echo "$FILES" | cut -d'|' -f2 | awk -F/ '{print $3}' | sort -u)
  for h in $hosts; do
    (
      echo "$FILES" | while IFS='|' read -r dest url lic; do
        [[ "$(echo "$url" | awk -F/ '{print $3}')" == "$h" ]] || continue
        fetch_one "$dest" "$url"
        [[ "$h" == "zfin.org" ]] && sleep 1
      done
    ) &
  done
  wait
fi

# integrity: gzip -t / tar -tzf (no content printed)
echo "$FILES" | while IFS='|' read -r dest url lic; do
  f="$dest/$(basename "$url")"
  [[ -f "$f" ]] || { echo "MISSING $f"; continue; }
  case "$f" in
    *.tar.gz) tar -tzf "$f" >/dev/null 2>&1 && echo "OK tar $f" || echo "BAD tar $f";;
    *.gz) gzip -t "$f" 2>/dev/null && echo "OK gz $f" || echo "BAD gz $f";;
  esac
done

if [[ "${1:-}" == "--verify" ]]; then
  shasum -a 256 -c "$SUMS"; exit $?
fi
# record hashes (committed file: hashes only) and manifest
echo "$FILES" | while IFS='|' read -r dest url lic; do f="$dest/$(basename "$url")"; [[ -f "$f" ]] && shasum -a 256 "$f"; done > "$SUMS"
echo "$FILES" > data/raw_db/_files.lst
python3 -I harness/fetch_db_manifest.py data/raw_db/_files.lst "$LOG" data/raw_db_manifest.json

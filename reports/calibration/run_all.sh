set -e
cd /Users/manav/bioelectric-bench/bioelectric-bench
P=reports/calibration/params_calib_nperm50.json
.venv/bin/python harness/calibrate_v2.py --setups skeleton --worlds null,class,vmem,lineage_only,dominant_lab,few_dir --variants real --modes agent,target,lab,decade --seeds 20 --params $P --workers 13 --out reports/calibration/calib_v2_skeleton.json > reports/calibration/calib_v2_skeleton.log 2>&1
.venv/bin/python harness/calibrate_v2.py --setups data/setups/setup_pass_derived/all_v3lookup.jsonl --worlds null,class --variants real,lin9 --modes agent,target --seeds 50 --params $P --workers 13 --out reports/calibration/calib_v2_setupmatrix.json > reports/calibration/calib_v2_setupmatrix.log 2>&1
echo ALLDONE > reports/calibration/done.flag

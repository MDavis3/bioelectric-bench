# Review of harness/dbtest.py against plans/pivot_db_v1.md (pre-seal)

Scope read: plans/pivot_db_v1.md, harness/dbtest.py, harness/db_blocks.py, config/db_params_v1.json,
data/db_setup/units_setup.csv, data/db_setup/nn_features.jsonl, sealed/SEALS.json (key names only).
Not opened: data/db_restricted, data/raw_db, data/restricted, reports/db_power_v1.*. No files edited.
Selftest: `SELFTEST OK` (null: 4 INCONCLUSIVE, 2 FAIL; planted: 6 PASS; 43 s).
All experiments below used the real setup files with synthetic outcomes only.

Result: 3 MUST, 9 SHOULD. The power simulation now running uses the solver in M1 and has to be re-run after
the patch (its result file is a sealed input and the code hash changes anyway).

## Checked and found correct

- T1 uses out-of-fold NN scores (`nn_score`): a unit's score uses only units in other folds, own block excluded;
  folds are grouped by block, so no unit sees its own or its block's outcome.
- T2: training NN scores (`nn_score_train`) and test NN scores both come from fold f's table (training units only);
  stratum base rates come from training units only; the ridge penalty is chosen inside the training fold; X is
  unpenalised in M2 (`pen_vec[1:][pen] = l2` writes through the view correctly); held-out set is class/control only.
- Direction of tests: permutation p counts `perm >= observed` with +1 correction; T2 is M1 minus M2 (positive = X
  helps); `exc_logor > 0`; FAIL uses the upper bound against log(1.5).
- Judge order matches H (UNTESTABLE, INVALID, PASS, FAIL, INCONCLUSIVE). IMPC floor: never causes UNTESTABLE on its
  own, drops only the IMPC condition, and says so in the reason. `None` sub-results block PASS (conservative).
- Setup floors on the real design: 394 class units (297 mouse, 97 zebrafish), 972 control, 50 class blocks,
  199 class units with IMPC. All floors met; the IMPC condition will be active.
- Folds: every fold has class units (19 to 63) and control units (34 to 125).
- S1 and leave-one-subclass-out masks select the intended units; 6 subclasses, class units only.
- Rehearsal shuffle indexing (`order[idx] = rng.permutation(idx)`; `y[order]`) is a correct within-stratum permutation.

## MUST

### M1. `logit_fit` diverges under quasi-separation and returns garbage X coefficients (dbtest.py:88-110)

Scenario: T1, its bootstrap, the permutations and every subset fit are unpenalised (ridge 1e-6) and include 11 IMPC
centre dummies. Several centres have very few class/control units (KMPC 8, MARC 5, ICS 10, RBRC 14), so "all Y = 0 in
that centre" is common, more so inside bootstrap resamples and subsets. The Newton loop has no step control, clips
eta at 30 and floors the weights at 1e-9, so the iteration leaves the optimum and never comes back; there is no
convergence check, so the value after 50 iterations is returned silently.

Measured on the real design (real E, random Y at a flat rate, random NN column; full fit + 100 block-bootstrap
resamples + mouse/zebrafish/IMPC subsets, 3 seeds per rate):

| Y rate | fits | X coefficient garbage (abs > 20) |
|---|---|---|
| 0.03 | 312 | 30 |
| 0.10 | 312 | 9 |
| 0.30 | 312 | 0 |

Examples of returned X log odds ratios: -1873104, +391646, +4213966 (true optimum -0.17, +0.10, +0.89). A further 51
fits differed from the converged solution by up to 0.34.

Consequences in the counted run: a garbage positive value in `or_impc`, `or_mouse`, an LOSO run or the point estimate
satisfies a PASS condition spuriously; garbage in the bootstrap corrupts `t1_lo`/`t1_hi` (spurious FAIL or lost
PASS); garbage in permutations shifts the p value. Y_exc is not affected in the same way only if its rate is high.
The selftest cannot see this (flat rate 0.25, `impc_center="none"`).

Patch (damped Newton on the penalised likelihood, stronger stabilising ridge, convergence reported). With this
version all 936 fits above converged:

```diff
-def logit_fit(X, y, l2=0.0, pen=None, iters=50):
+NONCONV = {"n": 0}
+
+def logit_fit(X, y, l2=0.0, pen=None, iters=100):
     n, p = X.shape
     Xa = np.column_stack([np.ones(n), X])
     pen_vec = np.zeros(p + 1)
     if pen is None:
         pen_vec[1:] = l2
     else:
         pen_vec[1:][pen] = l2
-    pen_vec[1:] += 1e-6          # tiny ridge for separation stability
+    pen_vec[1:] += 1e-4          # small ridge: finite optimum under separation and for constant columns
+
+    def obj(b):
+        eta = Xa @ b
+        return np.sum(np.logaddexp(0, eta) - y * eta) + 0.5 * np.sum(pen_vec * b * b)
     b = np.zeros(p + 1)
     ybar = np.clip(y.mean(), 1e-4, 1 - 1e-4)
     b[0] = np.log(ybar / (1 - ybar))
+    f = obj(b)
+    done = False
     for _ in range(iters):
-        eta = np.clip(Xa @ b, -30, 30)
-        mu = 1 / (1 + np.exp(-eta))
-        w = np.maximum(mu * (1 - mu), 1e-9)
+        mu = 1 / (1 + np.exp(-np.clip(Xa @ b, -700, 700)))
+        w = mu * (1 - mu)
         g = Xa.T @ (y - mu) - pen_vec * b
         H = (Xa * w[:, None]).T @ Xa + np.diag(pen_vec)
+        H[0, 0] += 1e-10
         step = np.linalg.solve(H, g)
-        b += step
-        if np.max(np.abs(step)) < 1e-8:
-            break
+        t = 1.0
+        while t > 1e-8:
+            fn = obj(b + t * step)
+            if fn <= f + 1e-12:
+                break
+            t /= 2
+        b = b + t * step
+        if f - fn < 1e-10 * (1 + abs(fn)):
+            done = True
+            break
+        f = fn
+    if not done:
+        NONCONV["n"] += 1
     return b
```

Also in `analyze`, before `return rep`: `rep["n_nonconverged_fits"] = NONCONV["n"]`, and in `main` refuse a verdict
(`INVALID`, "solver did not converge") if it is non-zero. Add a selftest case with IMPC centres of 5 to 10 units and
a Y rate of 0.05 that asserts every |log OR| < 10. Then re-run the power simulation.

### M2. The counted run is claimed before its inputs are validated, and missing outcomes become Y = 0 silently (dbtest.py:460-465, 473-477, 482, 493-509)

Scenarios:
- `o = ...reindex(s.unit_id)` then `fillna(0)`: any unit absent from the outcome file (id format mismatch for one
  species, a truncated file) is scored Y = 0, Y_exc = 0 with no message. If the gap differs by species or class this
  biases the only counted run. I could not inspect the outcome file, so this is unverified either way.
- `check_seals` creates the write-once marker, then computes `sha(outcome)`. Everything after that can still crash:
  outcome file missing (marker left empty), missing column, duplicate `unit_id` (reindex raises), simulation JSON
  without one of the four worlds (`sim["planted"]` KeyError, e.g. when `--worlds` was a subset), `--out` directory
  missing (raised after the full analysis, before the verdict is printed). In each case the run is burned and can
  only be repeated by deleting the marker by hand, which defeats the "one counted run" guarantee.

Patch: validate first, claim last, and write the result where the marker lives.

```diff
+def load_outcome(P, s):
+    o = pd.read_csv(ROOT / P["outcome"], dtype={"unit_id": str})
+    need = {"unit_id", "Y", "Y_exc", "lethal_nomorph"}
+    if not need <= set(o.columns):
+        sys.exit(f"refused: outcome file lacks {sorted(need - set(o.columns))}")
+    if o.unit_id.duplicated().any():
+        sys.exit("refused: duplicate unit_id in outcome file")
+    o = o.set_index("unit_id").reindex(s.unit_id)
+    miss = int(o[["Y", "Y_exc", "lethal_nomorph"]].isna().any(axis=1).sum())
+    if miss:
+        sys.exit(f"refused: {miss} setup units have no complete outcome row")
+    for c in ("Y", "Y_exc", "lethal_nomorph"):
+        if not set(np.unique(o[c].values)) <= {0, 1}:
+            sys.exit(f"refused: {c} is not 0/1")
+    return o
+
+def load_sim_gate(P, required):
+    if not P.get("simulation_result"):
+        if required:
+            sys.exit("refused: params name no simulation_result")
+        return True
+    sim = json.loads((ROOT / P["simulation_result"]).read_text())
+    worlds = ("null", "planted", "depth", "excitable")
+    if any(w not in sim or not sim[w].get("n") for w in worlds):
+        sys.exit("refused: simulation result lacks a world")
+    return (sim["planted"].get("PASS", 0) / sim["planted"]["n"] >= 0.8
+            and all(sim[w].get("PASS", 0) / sim[w]["n"] <= 0.05 for w in worlds if w != "planted"))
```

```diff
     # run
-    if a.mode == "counted":
-        check_seals(P, a.params)
-    o = pd.read_csv(ROOT / P["outcome"], dtype={"unit_id": str}).set_index("unit_id").reindex(s.unit_id)
-    y = o.Y.fillna(0).values.astype(float)
-    ye = o.Y_exc.fillna(0).values.astype(float)
-    le = o.lethal_nomorph.fillna(0).values.astype(float)
+    out = Path(a.out)
+    if not out.parent.is_dir() or out.exists():
+        sys.exit("refused: --out directory missing or file exists")
+    sim_ok = load_sim_gate(P, required=(a.mode == "counted"))
+    if a.mode == "counted":
+        check_seals(P, a.params)            # verification only, no marker yet
+    o = load_outcome(P, s)
+    if a.mode == "counted":
+        claim_counted(P)                    # the O_EXCL marker, moved out of check_seals; last step before analyze
+    y = o.Y.values.astype(float)
+    ye = o.Y_exc.values.astype(float)
+    le = o.lethal_nomorph.values.astype(float)
```

and delete lines 473-477 (the inline gate). `claim_counted` is lines 502-509 unchanged. If the missing-row check
fires because "unit with no outcome row" is a legitimate state in the outcome builder, fix the builder to write
explicit zeros rather than relaxing the check.

### M3. Rehearsal does not do what section I says, and it cannot exercise rule steps 3 to 5 (dbtest.py:466-472)

Section I: "One counted run, after a rehearsal on block-shuffled outcomes." The code permutes Y, Y_exc and
lethal_nomorph among individual units within species x source stratum. Differences that matter:
- Unit-level shuffling removes the within-block correlation of Y that the block bootstrap, the block permutation and
  the NN score depend on, so the rehearsal does not test the pipeline under the dependence structure of the real data.
- Y_exc is shuffled too, so the positive control fails by construction and `judge` returns INVALID about 97.5% of the
  time. PASS/FAIL/INCONCLUSIVE logic and the consistency conditions are never reached in the rehearsal verdict.
- Nothing forces a rehearsal to have happened before the counted run.

Patch (keeps real outcomes attached to their units, breaks the class link at block level, so the rehearsal is
"block-shuffled" in the sense of G's null; then report the verdict both ways):

```diff
-    if a.mode == "rehearsal":
-        # null rehearsal: outcomes permuted among units within each stratum (breaks any class link)
-        rng = np.random.default_rng(12345)
-        order = np.arange(len(s))
-        for _, idx in s.groupby("stratum").indices.items():
-            order[idx] = rng.permutation(idx)
-        y, ye, le = y[order], ye[order], le[order]
+    if a.mode == "rehearsal":
+        # null rehearsal: whole blocks exchange their outcome vectors' class link, i.e. cls is block-permuted
+        # within the same strata as the T1 null; outcomes stay with their units and blocks
+        rng = np.random.default_rng(12345)
+        cc = s.cls.isin(["class", "control"]).values
+        x = (s.cls == "class").astype(float).values
+        dt = pd.qcut(s.depth.rank(method="first"), 3, labels=False).values
+        xp = block_perm_x(s, x, cc, rng, dt)
+        s = s.copy()
+        s.loc[cc, "cls"] = np.where(xp[cc] == 1, "class", "control")
+        s.loc[cc & (xp == 0), "subclass"] = None
+        s.loc[cc & (xp == 1), "subclass"] = rng.choice(sorted(s.subclass.dropna().unique()), int((cc & (xp == 1)).sum()))
```

```diff
     v, why = judge(rep, P, sim_ok)
+    if a.mode == "rehearsal":
+        r2 = dict(rep, exc_logor=1.0, exc_p=0.0)
+        rep["verdict_if_positive_control_passed"] = judge(r2, P, sim_ok)[0]   # expected: not PASS
```

If the simpler current shuffle is preferred, the alternative is to change the sentence in section I to "a rehearsal
on outcomes shuffled among units within species x source" before sealing and still add the second verdict line; the
sealed text and the code must agree. Either way, have `claim_counted` refuse unless a rehearsal report with the same
`setup_sha256`, `params_sha256` and `outcome_sha256` exists (path as a CLI argument).

## SHOULD

### S1. Permutation strata are not the strata of section G (dbtest.py:256-267, 292)

- 168 of the 210 class/control blocks contain units from more than one species x source stratum (orthologs share a
  block), so "within species x source" cannot be applied to whole blocks. The code uses each block's most frequent
  stratum (ties broken by pandas order) and the rounded mean tertile. This is a reasonable reading but it is not what
  G says; state it in G.
- Depth tertiles are cut over all 20592 units, not over class/control: class/control units fall 261 / 633 / 472, and
  block cells are as small as 5 control + 0 class (mouse MGI-only, low depth) and 2 + 1.
- Block F4159 holds both class and control units (43% class). `int(round(mean))` labels it control in every
  permutation, while the observed statistic uses its real mixed labels.

```diff
-    g = sub.groupby("block").agg(x=("x", lambda v: int(round(v.mean()))),
-                                 st=("st", lambda v: v.value_counts().index[0]),
-                                 dt=("dt", lambda v: int(round(v.mean()))))
+    g = sub.groupby("block").agg(x=("x", lambda v: int(v.mean() >= 0.5)),
+                                 st=("st", lambda v: sorted(v.mode())[0]),
+                                 dt=("dt", "median"))
+    g["dt"] = pd.qcut(g.dt.rank(method="first"), 3, labels=False)     # tertiles of class/control blocks
```

and add to G: "strata are assigned per block: the block's most frequent species x source stratum and the tertile of
its median depth among class/control blocks; a block with both labels takes its majority label under permutation".
`block_perm_x` rebuilds the same groupby 6000 times; computing `g` once outside the loop cuts the counted run time.

### S2. Model definitions differ from G in two places (dbtest.py:200-204, 219-249)

- T1 is fully unpenalised, G says "covariates and NN score as in M1" (M1 is ridge with the CV penalty).
- T2 trains M1/M2 on class and control units only (`tr = (folds != f) & cc`); section C says other genes "train the
  NN and covariate models".
Both choices are defensible (the unpenalised T1 is the more standard one). Change the text rather than the code:
G, T1: "X, covariates and NN score unpenalised apart from a 1e-4 stabilising ridge"; G, T2: "M1 and M2 are fitted on
training-fold class and control units; other genes enter only through the NN score".

### S3. Inner CV for the ridge penalty reuses NN scores that saw the inner validation fold (dbtest.py:223-243)

`nn_tr` is computed once per outer fold; an inner validation unit's score uses outcomes of inner-training units and
vice versa, and its neighbours may sit in its own inner validation fold. No held-out outcome leaks (outer test units
are never used), so T2 stays valid; the penalty choice is slightly optimistic toward small lambda. Accept and note in
G, or rebuild neighbour tables per inner fold (costly).

### S4. Bootstrap bookkeeping (dbtest.py:304-313, 323-328)

Degenerate resamples are skipped without a count, a NaN in `boots` makes both bounds NaN (then silently
INCONCLUSIVE), and the NN column is held fixed across resamples (interval is conditional on the NN scores; say so).

```diff
     lo, hi = np.percentile(boots, [2.5, 97.5])
+    rep["t1_boot_used"] = len(boots)
+    if len(boots) < 0.95 * n_boot or not np.all(np.isfinite(boots)):
+        raise RuntimeError("T1 bootstrap degenerate")
```

(raise before the marker is irrelevant here, so pair this with M2's ordering and a rehearsal on the same data.)

### S5. `check_seals` gaps (dbtest.py:487-501)

- Sealed paths are hard-coded while the files actually read come from the params (`setup`, `feats`,
  `simulation_result`). Add `assert P["setup"] == SEALED_INPUTS["db_units_setup_v1"]` and the same for feats and the
  power file.
- `--params` is read relative to the working directory (line 442) but hashed relative to ROOT (line 500); run from
  another directory, a different file can be verified than the one used. Resolve once:
  `a.params = str(Path(a.params).resolve())` before both uses.
- Not verified although section I lists them as sealed first: `harness/db_blocks.py`,
  `config/db_endpoint_roots_v1.json`, `data/raw_db_manifest.json`, the eligibility/outcome-builder code. Add them to
  `SEALED_INPUTS`.
- The outcome file hash is recorded but not pinned. Have the subagent that builds it seal its hash
  (`db_outcome_v1`, hash only) and check it, so the file cannot change between rehearsal and counted run.

### S6. Judge: vacuous and implicit cases (dbtest.py:361-367)

`all(...)` over an empty `or_loso` is True (would pass if `subclass` failed to load), and `(v or -1) > 0` relies on
0.0 being falsy; NaN compares False silently.

```diff
+    def pos(v):
+        return v is not None and np.isfinite(v) and v > 0
     conds = {
 ...
-        "mouse>0": (rep["or_mouse"] or -1) > 0,
-        "zebrafish>0": (rep["or_zebrafish"] or -1) > 0,
-        "s1>0": (rep["or_s1"] or -1) > 0,
-        "loso>0": all((v if v is not None else -1) > 0 for v in rep["or_loso"].values()),
+        "mouse>0": pos(rep["or_mouse"]),
+        "zebrafish>0": pos(rep["or_zebrafish"]),
+        "s1>0": pos(rep["or_s1"]),
+        "loso>0": len(rep["or_loso"]) == 6 and all(pos(v) for v in rep["or_loso"].values()),
     }
     if impc_ok:
-        conds["impc>0"] = (rep["or_impc"] or -1) > 0
+        conds["impc>0"] = pos(rep["or_impc"])
```

### S7. Subset fits keep columns that are constant in the subset (dbtest.py:330-334)

In the zebrafish subset 14 of 18 covariate columns are constant; in the IMPC subset `src_impc` is constant. The fit
then depends on the stabilising ridge to be solvable. With M1's patch this is safe; cleaner:

```diff
-        return float(t1_fit(E, nns, x, y, m))
+        keep = E[m].std(0) > 0
+        return float(t1_fit(E[:, keep], nns, x, y, m))
```

### S8. Expression features are not mapped to Uberon (data/db_setup/nn_features.jsonl; prereg D)

All mouse `expr` terms are EMAPA ids and all zebrafish terms are ZFA ids, so the expression Jaccard between a mouse
and a zebrafish unit is always 0 and cross-species neighbours are ranked on two of three components. D says "mapped
to Uberon". This weakens the NN baseline (which makes the class effect easier to show), so either remap before
sealing or log it as a substitution in K. Also 2638 zebrafish and 1105 mouse units have no molecular-function terms
and fall back toward the base rate.

### S9. Simulation fidelity (dbtest.py:377-396, 445-446)

- A stratum key in `--rates` that does not match `species|abc` falls back to the mean rate silently; assert
  `set(rates) == set(s.stratum.unique())`.
- Adding the block effect and depth term on the logit scale moves the simulated marginal rate away from the observed
  one (toward 0.5 for low rates), so the simulation sees less separation than the real run will (see M1).
- `ProcessPoolExecutor` with fork: a worker exception surfaces only at the end of a world; fine, but the per-world
  dict silently lacks verdict keys that never occurred (handled by `.get`).

## Order of work

1. Apply M1, M2, M3 (and S1, S6, S7 while the file is open); run selftest.
2. Re-run the power simulation with the patched code; if the null/confound worlds changed, review before sealing.
3. Amend prereg text for M3 (if the text route is taken), S1, S2, S3, S8.
4. Seal; rehearsal; counted run.

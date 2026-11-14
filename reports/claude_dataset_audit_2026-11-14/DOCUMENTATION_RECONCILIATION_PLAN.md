# Documentation Reconciliation Plan: First Kaggle Walk-Forward Experiment

**Written:** 2026-11-14 (IST). **Mode:** read-only. No documentation, script, dataset or decision was changed; nothing was committed or pushed. This file is a proposal awaiting the project owner's approval.

## Evidence base

| Tag | Source |
|---|---|
| **NB n** | Saved source/output of cell *n* (0-based) of `~/Desktop/Northgate - Stock Predictor/notebookf887dc542c.ipynb` (SHA-256 `5e2374b5…25aa7e`) |
| **REC §n** | `reports/claude_dataset_audit_2026-11-14/NORTHGATE_EXPERIMENT_RECOVERY.md`, section *n* |
| **Docs** | GitHub `origin/main` at commit `62e5272` (2026-11-14 04:35 IST). Line numbers refer to that commit |

Note: the local working tree is at `39bbc63`, 319 commits behind. Its copies of these documents predate the experiment entirely. All corrections below target the GitHub versions; the local clone must be synchronised first (step 0 of the order at the end).

**Classification used for every item:** **CONFIRMED** = the notebook settles it; **UNRESOLVED** = the notebook cannot settle it; **CLARIFICATION** = the document is not wrong but will mislead a reader about what was executed.

**Proposed editing convention** (matches `docs/CONTINUITY_PROTOCOL.md` rules 4, 7 and the project's practice of dated entries): do not rewrite or delete earlier entries. Append one dated correction entry per file, and add a one-line pointer "(corrected 2026-11-14, see below)" next to each superseded sentence only where a reader would otherwise be misled.

---

## Part A. Proposed corrections

### A1. Dataset identity, row counts and split sizes

**R-01. The experiment did not use the existing CSVs.** CONFIRMED.
* **File / section:** `STATUS.md` line 12 ("Project state") and line 608; `PROJECT_NOTEBOOK.md` line 52, line 201 and line 244.
* **Current statement:** "…completed in Kaggle on the existing train/validation data" (STATUS 12); "executed in Kaggle … using the existing training and validation CSVs" (NOTEBOOK 201); "It used the existing price/volume-only Yahoo-derived dataset" (NOTEBOOK 244).
* **Notebook evidence:** the session cloned the repo and ran `scripts/prepare_gpu_training_data.py`, which downloads from Yahoo and rebuilds everything (NB 15, 28). Output: market rows 29,506; labelled rows 29,495; splits 21,708 / 6,390 / 1,397 (NB 15, 52). The Mac files documented at STATUS line 68 are 29,484 / 29,473 and 21,708 / 6,379 / 1,386.
* **Proposed correction:** "The experiment ran on a dataset rebuilt inside the Kaggle session from a fresh Yahoo download using `prepare_gpu_training_data.py` (29,506 market rows; 29,495 labelled; train 21,708 / validation 6,390 / test 1,397). It is a different download, with a different feature set, from the Mac files (29,484; 29,473; 21,708 / 6,379 / 1,386). The Kaggle data files were not preserved."
* **Why it matters:** results are being attributed to a dataset that did not produce them. Anyone re-running on the Mac CSVs would get a different feature set and one fewer validation session.

**R-02. Record both sets of counts side by side wherever counts appear as "the" dataset.** CLARIFICATION.
* **File / section:** `STATUS.md` line 68 (splits) and the 2026-11-14 walk-forward entry (lines 602–610); `docs/MODEL_TRAINING_GUIDE.md` §3–4.
* **Current statement:** only the Mac counts are documented anywhere.
* **Notebook evidence:** NB 15, 52, 69 (equity-only rows used: training 19,740; validation 5,810).
* **Proposed correction:** add a two-column table "Mac build (2026-11-12)" vs "Kaggle build (experiment)" with market rows, labelled rows, splits, feature-date ranges and equity-only counts.
* **Why it matters:** prevents silent mixing of the two datasets in later comparisons.

**R-03. The test boundary differed between the two builds.** CONFIRMED (fact); the consequence is a decision for the owner.
* **File / section:** `DECISIONS.md` line 64; `STATUS.md` lines 62, 68; `PROJECT_NOTEBOOK.md` line 62.
* **Current statement:** "calculate the final test cutoff from the latest available target date at dataset-build time… For the currently reported latest target date of 2026-11-09, the calendar cutoff is 2026-05-09" (DECISIONS 64); test target dates 2026-05-11 → 2026-11-09 (STATUS 68).
* **Notebook evidence:** Kaggle test feature dates run 2026-05-11 → 2026-11-11 and validation feature dates end 2026-05-08 (NB 52), so the row with feature date 2026-05-08 (target 2026-05-11) is validation on Kaggle and test on the Mac. Validation 6,390 vs 6,379 = one session × 11 instruments.
* **Proposed correction:** do **not** edit the decision. Add a dated note under it: "Observed consequence: because the cutoff is recomputed from the newest row, the Kaggle rebuild placed target date 2026-05-11 in validation while the Mac build places it in test. Ten equity rows of the Mac test partition were therefore scored as validation in Experiment 01. Whether to freeze absolute dates is an open decision." Add the question to `QUESTIONS.md`.
* **Why it matters:** "the sealed test partition" is not a single fixed set of rows across builds.

### A2. Target variable and prediction horizon

**R-04. Executed training target was log return for all eight models.** CONFIRMED.
* **File / section:** `docs/MODEL_TRAINING_GUIDE.md` line 38 (§3) and line 119 (§7); `STATUS.md` line 189; `DECISIONS.md` line 54 (context only).
* **Current statement:** "Target: the same instrument's next observed trading session adjusted close; next-session log return and direction are retained as related labels" (GUIDE 38); "The classical script's MAE/RMSE/MAPE/R² are computed on adjusted-close levels; the deep script predicts log returns…" (GUIDE 119).
* **Notebook evidence:** classical target switched to `target_log_return_t1` by an in-session patch (NB 39); walk-forward `TARGET = "target_log_return_t1"` and report field `"target": "target_log_return_t1"` (NB 70, 75). Prices for metrics are rebuilt as `Adj Close × exp(return)`.
* **Proposed correction:** in the guide, add: "Experiment 01 as executed trained every model on next-session log return and derived adjusted-close predictions from it. The committed `train_baseline_models.py` still regresses the price level; that version produced MAE 38–819 and negative R² for three models on Kaggle (NB 16) and was abandoned in-session."
* **Why it matters:** the documented and executed targets differ; the committed classical script reproduces a failed configuration, not the reported one.

**R-05. The log-return target is an executed choice, not a recorded decision.** CLARIFICATION.
* **File / section:** `DECISIONS.md` line 54 ("First forecasting target follows the PRD").
* **Current statement:** primary target is next-session adjusted close; log return and direction "retained as derived labels/evaluation fields".
* **Notebook evidence:** as R-04.
* **Proposed correction:** leave the decision text untouched. Add under "Not decisions" (or a new "Executed but not decided" list): "Experiment 01 trained on next-session log return and reported reconstructed prices. This was an experimental choice made in the Kaggle session; it has not been approved as a change to the target decision."
* **Why it matters:** keeps the decisions log honest (`CONTINUITY_PROTOCOL.md` rule 3) and stops a session-level choice becoming a de-facto decision.

**R-06. Horizon.** No discrepancy: one session ahead in documents and notebook. Record explicitly that no multi-day label was built or used (NB 70 has only `target_log_return_t1`). CONFIRMED.

### A3. Feature count and definitions

**R-07. 25 model inputs, not 24.** CONFIRMED.
* **File / section:** `STATUS.md` line 204; `PROJECT_NOTEBOOK.md` line 244; `docs/MODEL_TRAINING_GUIDE.md` line 37.
* **Current statement:** "24 backward-looking … features".
* **Notebook evidence:** build reports `feature_count: 24` (NB 15); the training programs use 25 = those 24 plus raw `Adj Close` (NB 67, 69, 75); the program aborts unless exactly 25 are found (NB 70).
* **Proposed correction:** "24 engineered features plus the raw `Adj Close` level = 25 model inputs; deep models also receive a 10-element one-hot ticker indicator."
* **Why it matters:** `Adj Close` as an input is a material modelling choice (a restated price level) that the documents do not disclose.

**R-08. Two different "24-feature" sets exist under the same name.** CONFIRMED.
* **File / section:** `STATUS.md` line 11 and `PROJECT_NOTEBOOK.md` line 49 (Mac features) versus `STATUS.md` line 204 and `MODEL_TRAINING_GUIDE.md` line 37 (GPU features).
* **Current statement:** both described only as "24 … features".
* **Notebook evidence:** experiment features are `return_1d…20d`, `price_sma_ratio_5…200`, `price_ema_ratio_12/26`, `volatility_5d…60d`, `rsi_14`, `macd_pct`, `macd_signal_pct`, `atr_14_pct`, `volume_sma_ratio_20`, `volume_change_1d`, `obv_change_20` (NB 67). The Mac `feature_panel.csv` has `log_return_1d` and lags, `sma_*`, `price_to_sma_*`, `ema_12/26`, `macd`, `rsi_14`, `volatility_20d`, `bollinger_width_20`, three volume features and `adj_close_vs_close` (verified in the dataset audit).
* **Proposed correction:** name the two sets ("Mac feature set v0", "GPU feature set v1") and list the experiment's 25 inputs verbatim in the guide.
* **Why it matters:** "24 features" currently refers to two incompatible datasets.

**R-09. `atr_14_pct` was redefined in-session.** CONFIRMED.
* **File / section:** no document mentions it; add to the walk-forward entries in `STATUS.md` / `PROJECT_NOTEBOOK.md`.
* **Notebook evidence:** NB 26 replaced the committed formula (High/Low/Close range divided by `Adj Close`) with a range built from High/Low rescaled by `Adj Close / Close`; data was rebuilt afterwards (NB 28).
* **Proposed correction:** state that the experiment used the patched ATR and that the committed script still contains the unpatched formula.
* **Why it matters:** one of the 25 inputs cannot be regenerated from the repository.

**R-10. Raw columns excluded in-session.** CONFIRMED.
* **Notebook evidence:** `Open, High, Low, Close, Volume, Dividends, Stock Splits` excluded by patches (NB 27, 32) and by `EXCLUDED` (NB 70). The committed scripts select all numeric columns (32 features on first run, NB 16).
* **Proposed correction:** document the exclusion list in the guide as executed behaviour.
* **Why it matters:** same reproducibility gap as R-09.

### A4. Model hyperparameters

**R-11. Batch and hidden sizes.** CONFIRMED.
* **File / section:** `docs/MODEL_TRAINING_GUIDE.md` line 99; `STATUS.md` line 224; `docs/GPU_LAPTOP_SETUP.md` line 22.
* **Current statement:** "sequence length 30, batch size 16, hidden size 32".
* **Notebook evidence:** `sequence_length 30, batch_size 8, hidden_size 24, epochs_max 30, patience 6` (NB 72, 75).
* **Proposed correction:** "Experiment 01 ran with batch 8 and hidden 24 (the script defaults remain 16 and 32)."
* **Why it matters:** the documented defaults are not the reported configuration.

**R-12. No tuning; one seed.** CLARIFICATION.
* **File / section:** `STATUS.md` 602–610; `PROJECT_NOTEBOOK.md` 200–237 (limitations list).
* **Current statement:** limitations listed do not mention tuning or seeds.
* **Notebook evidence:** fixed values for every model (Ridge alpha 10; RF 120 trees; SVR C 1, epsilon 0.01; XGBoost 250 trees, depth 4, lr 0.04); `SEED = 42`, one run each (NB 70).
* **Proposed correction:** add to limitations: "No hyper-parameter tuning was performed and each model was run once with seed 42; no confidence intervals exist."
* **Why it matters:** the PRD requires tuned models; small differences are otherwise over-read.

**R-13. Record the selected epochs.** CLARIFICATION. Add the 5 × 4 table of inner-stopping epochs (REC §4, NB 72). They exist nowhere else and the checkpoints are not held.

### A5. Validation methodology

**R-14. Deep models used an inner stopping split and refit; the committed deep script does not.** CONFIRMED.
* **File / section:** `docs/MODEL_TRAINING_GUIDE.md` §4–5 (lines 45–99); `STATUS.md` line 206.
* **Current statement:** "Use validation data for early stopping and model selection."
* **Notebook evidence:** walk-forward uses the last 15 % of each fold's training dates for early stopping, refits on full fold training data, then scores validation once (NB 70 `run_deep_fold`; `inner_stopping_fraction 0.15`, NB 75).
* **Proposed correction:** describe the executed three-stage procedure; state that the committed `train_deep_models.py` instead stops on the same validation set it reports.
* **Why it matters:** the executed method is stricter than the documented one, and the repository holds only the weaker version.

**R-15. Classical models per ticker, deep models pooled.** CLARIFICATION.
* **File / section:** `STATUS.md` 602–610; `PROJECT_NOTEBOOK.md` 200–237.
* **Notebook evidence:** NB 70 (`train_classical_fold` loops over tickers; `make_sequences` pools tickers with a one-hot).
* **Proposed correction:** add one sentence to both entries.
* **Why it matters:** the comparison is not like-for-like in model scope.

**R-16. Fold construction details.** CLARIFICATION.
* **Notebook evidence:** folds are assigned by feature `Date`; validation rows sum to 5,800 of 5,810 because the 10 rows dated 2023-12-29 are used as training; the "2026-YTD" window is coded to 2026-06-01 but data ends 2026-05-08; fold rows 1,200 / 1,260 / 1,230 / 1,260 / 850 (NB 69–71).
* **Proposed correction:** add the fold table from REC §5 to `PROJECT_NOTEBOOK.md`.
* **Why it matters:** needed to reproduce the 500 rows exactly.

### A6. Baselines and metrics

**R-17. Explanation of the naive baseline's 0.495 % directional accuracy is wrong.** CONFIRMED.
* **File / section:** `PROJECT_NOTEBOOK.md` line 225 (and the pointer in `STATUS.md` commit "Clarify zero-return baseline directional metric").
* **Current statement:** "a zero forecast is classified as non-positive/down by the binary direction rule, so this number mostly reflects the frequency of down days".
* **Notebook evidence:** metric is `mean(sign(y_true) == sign(direction))` (NB 70). `sign(0) = 0`, so it matches only exact-zero returns: 26 of 5,810 validation rows = 0.4475 % (NB 46). Down days are 50.34 % (NB 44).
* **Proposed correction:** "The direction metric is a three-way sign comparison. A zero forecast has sign 0 and is counted correct only on days with exactly zero return (26 of 5,810 validation rows). It is not the frequency of down days."
* **Why it matters:** the current text describes a different metric from the one that ran.

**R-18. "Pooled price MAE" is an unweighted mean of 50 per-ticker-fold MAEs.** CONFIRMED.
* **File / section:** `STATUS.md` lines 12, 605, 607; `PROJECT_NOTEBOOK.md` lines 210, 225, 231.
* **Notebook evidence:** `frame.groupby("model")[metric_cols].mean()` over 50 rows per model (NB 70 `save_summary`).
* **Proposed correction:** replace "pooled" with "mean of the 50 per-(ticker, fold) values, in rupees, unweighted" in a correction note; keep the existing caution that price scales differ.
* **Why it matters:** "pooled" implies a row-level error over all predictions, which was not computed.

**R-19. Direction and price metrics are defined differently in committed vs executed code.** CLARIFICATION.
* **File / section:** `docs/MODEL_TRAINING_GUIDE.md` line 119.
* **Notebook evidence:** executed code uses one function for all models (NB 39, 70); committed classical script compares price to current price (`train_baseline_models.py:72-73`).
* **Proposed correction:** note that Experiment 01 used the unified definition.

**R-20. Two baselines existed only in the executed code.** CONFIRMED. `Always_Up_Direction_Baseline` and the zero-return form of `Naive_Last_Adjusted_Close` were introduced by NB 39/70; the committed script has only the price-level naive. Add to the guide.

**R-21. Overall R² ≈ 0.90 vs ≈ 0.977 / 0.999 in earlier runs.** CLARIFICATION. Three different aggregation scopes appear in the notebook (mean per ticker-fold; mean per ticker; pooled over all rows). Add a sentence that R² values from the three runs are not comparable (REC §15 L13).

### A7. Test-partition handling

**R-22. "Not loaded" is true for training and evaluation code, incomplete for the session.** CONFIRMED.
* **File / section:** `STATUS.md` lines 12, 604, 608; `PROJECT_NOTEBOOK.md` lines 52, 206, 208, 233.
* **Current statement:** "The final test partition was not loaded (`test_partition_loaded=false`)".
* **Notebook evidence:** the walk-forward program and both training scripts never read `test.csv`, and the flag is a literal written by the program (NB 70). Separately, NB 52 read `test.csv` to print rows (1,397), feature-date range and tickers; NB 18 ran `describe()` on the full 29,495-row dataset including target columns; NB 23 printed per-ticker adjustment-ratio statistics over all rows. No test metric was computed.
* **Proposed correction:** "No training or evaluation code loaded the test partition and no test metric was computed. `test_partition_loaded=false` is a constant written by the program, consistent with its code. In the same session `test.csv` was opened once to print its row count, date range and tickers, and whole-dataset descriptive statistics were displayed."
* **Why it matters:** an auditor who finds cell 52 after reading "not loaded" would doubt the rest of the record. Full disclosure costs nothing.

### A8. Reproducibility and artifacts

**R-23. Executed code is not in the repository.** CONFIRMED.
* **File / section:** `STATUS.md` 602–610; `PROJECT_NOTEBOOK.md` line 242 ("The repository training guide and scripts define the first price/volume-only experiment"); `docs/MODEL_TRAINING_GUIDE.md` §5–6.
* **Notebook evidence:** `git status` in-session shows three modified scripts and untracked outputs at commit `df50a7c` (NB 60); `run_walk_forward.py` was created by `%%writefile` (NB 70).
* **Proposed correction:** "The repository scripts do **not** define Experiment 01. It ran three scripts patched in the Kaggle session and a new `run_walk_forward.py`, none of which is committed. The code survives as text in the notebook `notebookf887dc542c.ipynb`."
* **Why it matters:** the current sentence asserts reproducibility that does not exist.

**R-24. Artifact status.** CONFIRMED (as of this audit).
* **File / section:** `STATUS.md` line 609; `PROJECT_NOTEBOOK.md` line 234; `MODEL_TRAINING_GUIDE.md` lines 105–111.
* **Current statement:** "Generated Kaggle outputs/checkpoints were verified in the user's session but have not been confirmed committed to GitHub."
* **Notebook evidence:** listing of 5 report files and 20 checkpoints with sizes (NB 78). None exists locally or on GitHub.
* **Proposed correction:** "As of 2026-11-14 none of the 5 report files or 20 checkpoints is held outside Kaggle. The notebook preserves the full `model_summary`, `fold_model_summary` and run report as printed text, but only 5 of 500 `fold_results` rows and 10 of 80 per-stock rows." Add actual output paths (`reports/walk_forward/`, `models/walk_forward/`) to the guide, which lists only `reports/validation/` and `models/deep/`.
* **Why it matters:** sets the correct expectation about what can still be analysed.

**R-25. Environment facts to record.** CLARIFICATION. Python 3.13 on Kaggle (project guide specifies 3.11; the Mac ran 3.14); repo commit `df50a7c`; duration 4,986.31 s; XGBoost device-mismatch warning with no CPU fallback rows (NB 72, 74, 75).

### A9. Statements that became stale

**R-26. "No model has been trained" statements.** CLARIFICATION.
* **File / section:** `STATUS.md` lines 55, 63, 72, 192, 309; `docs/IMPLEMENTATION_PLAN.md` line 112.
* **Status:** already superseded by dated notes (`PROJECT_NOTEBOOK.md` 242; `IMPLEMENTATION_PLAN.md` 129). No rewrite needed. Optional: add "(historical; superseded 2026-11-14)" beside STATUS lines 192 and 309, which sit far from the superseding entry.

---

## Part B. Contradictions to keep documented, not overwrite

1. **Decision vs execution on the target.** `DECISIONS.md` says adjusted close; the experiment trained on log return. Keep both, flagged as unresolved (R-05).
2. **Decision vs consequence on the test cutoff.** The "compute from latest date" decision stands as written; its observed side-effect is recorded beside it (R-03).
3. **Two datasets.** Mac build and Kaggle build both stay documented with their own counts (R-02). Neither replaces the other.
4. **Two feature sets and committed vs executed code.** Document both; do not edit the guide to pretend the committed scripts match the run (R-08, R-23).
5. **Notebook metadata vs logs.** Metadata says `accelerator: none`, `isGpuEnabled: false`, `isInternetEnabled: false`; logs show a Tesla T4, a successful clone and downloads. Record both.
6. **Suspicious results.** Transformer 2024-H2 MAE 17.853813 vs naive 17.853815 counted as a "win"; several deep models with directional accuracy identical to always-up or to each other in a fold; single-split BiLSTM MAE 17.988 below naive 17.997 under a different aggregation. Keep as open items (REC §15 L5, L6, L13).
7. **Earlier single-split runs.** The failed price-level runs (Ridge 38.3; RandomForest 222.9; XGBoost 233.6; SVR 819.2) and the intermediate runs are part of the record and should be mentioned, not omitted.
8. **Historical "not yet run" entries** remain as history (R-26).

## Part C. Unresolved questions (cannot be settled from the notebook)

| # | Question | What would settle it |
|---|---|---|
| U-1 | Do the Kaggle outputs (5 reports, 20 checkpoints, data files) still exist? | Owner checks the Kaggle session / saved version |
| U-2 | Which 3 stocks does BiLSTM beat naive on, and which 1 for GRU and Transformer? Only BHARTIARTL/BiLSTM is visible | `fold_results.csv` |
| U-3 | Are the Transformer and some recurrent models emitting near-constant predictions (Part B item 6)? | Predictions or checkpoints |
| U-4 | How much do the 26 exact-zero-return rows (stale/phantom bars) affect the metrics? | `fold_results.csv` plus the Kaggle dataset, or a rerun on corrected data |
| U-5 | How different is the Kaggle download from the Mac download beyond the extra sessions? | The Kaggle `market_panel.csv` |
| U-6 | Should the log-return target be adopted as a decision? | Owner decision |
| U-7 | Should the test boundary be frozen as absolute dates, and is 2026-05-11 test or validation? | Owner decision |
| U-8 | Why the notebook metadata disagrees with the logs | Kaggle version history |
| U-9 | Is the notebook on Kaggle the same version as the local file? | Compare on Kaggle |

## Part D. Recommended order of correction

0. **Synchronise the local clone with GitHub** (`git pull --ff-only`). Without this, edits would be made to documents 319 commits out of date.
1. **`STATUS.md`:** append one dated correction entry covering R-01, R-02, R-18, R-22, R-23, R-24, R-12, R-15. This is the file every session reads first.
2. **`PROJECT_NOTEBOOK.md`:** append the matching entry, adding R-17 (direction explanation), R-16 (fold table), R-13 (epochs), R-07/R-08 (features) and Part B items 5–7. Add pointers at lines 201, 225, 242, 244.
3. **`DECISIONS.md`:** add the two "executed but not decided" notes (R-03, R-05). Change no decision.
4. **`QUESTIONS.md`:** add U-1 to U-9.
5. **`docs/MODEL_TRAINING_GUIDE.md`:** add a section "Experiment 01 as executed" (R-04, R-07, R-09, R-10, R-11, R-14, R-19, R-20, R-24, R-25), leaving the description of the committed scripts intact and clearly labelled as such.
6. **`docs/GPU_LAPTOP_SETUP.md` and `docs/IMPLEMENTATION_PLAN.md`:** one-line pointers only (R-11, R-26).
7. **`docs/CONTINUITY_PROTOCOL.md`:** no correction needed. Optional addition for the owner to consider: "Record the dataset build (row counts, download date) and the commit plus any uncommitted changes with every experiment."
8. After the edits, re-fetch each changed file and verify it (protocol rule 8).

Steps 1–2 fix every statement that is currently wrong; steps 3–7 are clarifications.

**No change has been made. Awaiting approval.**

# Decisions Required From the Project Owner

18 decisions. Each lists options, trade-offs, my recommendation (labelled as mine) and what is blocked until you decide. Nothing here has been decided or implemented. Order = urgency.

| # | Decision | Blocks |
|---|---|---|
| D-15 | What is submitted on 15 Nov 2026 | everything scheduled |
| D-02 | Price basis / target definition | all new training |
| D-03 | Policy for labels that cross corporate actions | next experiment |
| D-04 | Freeze split as absolute dates | next experiment, final test |
| D-05 | Treatment of the 19 stale/phantom rows | dataset v2 |
| D-06 | Treatment of special/muhurat sessions | dataset v2 |
| D-01 | Prediction timestamp | features, news alignment, backtest |
| D-17 | Metrics and direction convention | evaluation protocol |
| D-14 | Data rights and NSE route | official price rebuild, announcements |
| D-08 | Portfolio benchmark | backtest |
| D-07 | Universe definition and survivorship statement | final test, report |
| D-10 | CPI: extend or drop | macro block |
| D-09 | US FRED series: include as named in PRD? | macro block |
| D-11 | News source | sentiment |
| D-12 | Sentiment licence and text storage | sentiment |
| D-13 | Multi-day horizons | labels, purge |
| D-16 | Split ratios: PRD 70/15/15 vs agreed target-date split | report wording |
| D-18 | Transaction-cost assumptions | backtest |

---

### D-15 What to submit on 15 November 2026 (tomorrow)
Remaining work in `REMAINING_TASKS.csv` is about 40–55 working days if done to the PRD's standard (my estimate, ±30 %); most sit in P2/P3 and cannot be done by tomorrow.
* **Option 1: Submit an honest partial** (data audit + corrected pipeline + Experiment 01 labelled exploratory + limitations). Fast, defensible, the PRD grades honesty ("a modest, correct, leakage-free result … scores higher").
* **Option 2: Ask for an extension** and complete P0+P1 and the experiments.
* **Option 3: Rush all PRD parts** on the current data. High risk: the portfolio/backtest would inherit unresolved basis and calendar defects.
**Recommendation (mine): 1 now, 2 if the deadline can move.** Blocks: sequencing of everything.

### D-02 Price basis and target definition
See `CORPORATE_ACTION_AUDIT.md` §8, options A–E. **Recommendation (mine): C** (next-session log return on the existing vendor series, two artefact events flagged, sensitivity arm; PRD price reported as `P_t·exp(r̂)`); schedule D only for validation. Alternative if you must stay PRD-literal: A, accepting restated levels. **Blocks:** any retraining, T-006.

### D-03 Labels crossing unresolved corporate actions
Options: (a) keep and flag; (b) exclude the label rows for ITC 2025-01-03 and HINDUNILVR 2025-12-04 (and the matching feature windows); (c) replace with a shareholder-wealth label after T-011. **Recommendation (mine): (a) in the main run + (b) as a sensitivity arm, (c) only if T-011 yields official values.** Blocks: Experiment 02.

### D-04 Freeze the split as absolute dates
The test start moves with the data (finding L-01). Option 1: freeze train ≤ 2023-12-31, validation 2024-01-01 → 2026-05-08, test 2026-05-11 → 2026-11-09 (the Mac values, already reported in documents). Option 2: re-cut after the data repair (rows change). **Recommendation (mine): option 1 unless D-05/D-06 change dates; stamp with a `data_snapshot_id`.** Note the test is already partly "seen" only in the sense of row counts; no outcomes were inspected. Blocks: any new run, final test.

### D-05 The 19 stale/phantom bars
Phantom session 2026-01-15 (NSE closed for municipal elections; 10 rows) and stale 2025-03-18 (9 tickers flat with zero volume). Options: (a) drop all 19 rows; (b) replace 2025-03-18 with official NSE prices (one file) and drop 2026-01-15; (c) keep with a flag. **Recommendation (mine): (b)**, because it removes 19 false labels (73 % of all zero-return labels in validation) at the cost of one manual download. Blocks: dataset v2.

### D-06 Special sessions (Muhurat, Saturday/Sunday live sessions)
Seven real sessions are missing for equities in the panel; the index has them missing for different dates. Options: (a) include all real sessions using official files; (b) exclude all special sessions for every instrument and document. **Recommendation (mine): (b)** for the baseline (fewest manual downloads; special sessions have atypical liquidity), revisit if you adopt D. Blocks: calendar table.

### D-01 Prediction timestamp
Current design = decision after the close of day *t* using day-*t* OHLCV, predicting the close of *t+1* (an entry at the close of *t* is implicitly assumed in any backtest). Alternative = before the open of *t+1* with the same inputs (same information, different execution price: open of *t+1*). **Recommendation (mine): keep after-close prediction; define the backtest entry as the *t+1 open* or the *t+1 close* explicitly (the PRD does not say).** This also fixes news and CPI alignment (15:30 IST cut-off, next session). Blocks: news mapping, backtest.

### D-17 Metrics and direction convention
Experiment 01's headline "pooled price MAE" is dominated by LT and TCS (41 % of naive error), and its directional metric is ternary. **Proposal:** primary = per-ticker MAE of log return and skill vs naive, averaged equally across tickers; direction on non-zero labels only; also report the PRD's RMSE/MAE/MAPE/R²/directional accuracy; paired block-bootstrap intervals. **Recommendation (mine): adopt as stated.** Blocks: T-020.

### D-14 Data rights and NSE route
NSE's terms restrict systematic automated collection and simulation use; the files you downloaded were fetched by script. Options: (1) manual exports only (Security-wise Archive, Corporate Actions, Indices, VIX; ≈ 40 exports); (2) apply through NSE Data for Research (needs an eligible institution); (3) treat NSE as validation only, never as stored model input; (4) licensed vendor. **Recommendation (mine): (1)+(3)** for validation, keep files private/untracked, record terms in `docs/DATA_RIGHTS.md`, and do not extend the scripted downloader. Blocks: T-012, T-101, T-110.

### D-08 Portfolio benchmark
PRD allows NIFTY 50 (`^NSEI`). The price index excludes dividends (≈ 1.2–1.5 % a year, my estimate), while `Adj Close` portfolios include them. **Recommendation (mine): NIFTY 50 TRI as the benchmark; show the price index as a secondary line.** Blocks: backtest.

### D-07 Universe and survivorship
Ten current large caps, chosen in 2026, no stated rule. Options: (a) declare a fixed **case-study universe** (named, with listing dates and NIFTY membership dates) and state the limitation; (b) rebuild a point-in-time universe (needs delisted data; not obtainable free with confidence). **Recommendation (mine): (a).** Do not claim generalisation to other stocks. Blocks: report text, final test.

### D-10 CPI
Present coverage: 0 training rows, 20.7 % of the panel, ends at Dec 2025. Options: (a) extend release events back to 2015 (≈ 1.5–2 days, headline provisional/final values only); (b) restrict the CPI ablation to 2024-08 → 2026 and say so; (c) drop CPI. **Recommendation (mine): (a) if D-15 allows time, otherwise (c) and report the CPI pipeline as built-and-tested but unused.** Blocks: macro block.

### D-09 US series named by the PRD (DGS10, DGS3MO, CPIAUCSL, UNRATE, VIX)
Options: include as named (lagged, ALFRED first-release for CPIAUCSL/UNRATE; needs a free FRED key) or replace by Indian equivalents with a written scope note. **Recommendation (mine): include DGS10, DGS3MO, VIX (daily, one-session lag); add repo rate, USD/INR and India VIX; treat CPIAUCSL/UNRATE as low-priority.** Blocks: macro block.

### D-11 News source
Candidates: GDELT GKG on BigQuery (free tier, metadata and tone, noisy entity matching), NSE announcements (exact timestamps, manual export), paid APIs (not free). **Recommendation (mine): run the one-day pilot T-108; if it passes, use GDELT as the media layer and NSE announcements as the event layer; if not, report news as infeasible within free sources.** Requires a Google Cloud account from you. Blocks: sentiment.

### D-12 Sentiment licence and text storage
FinBERT weights are CC BY-NC-SA 4.0 (non-commercial); VADER is MIT. Publisher terms forbid storing article text. **Recommendation (mine): use FinBERT for this academic, non-commercial project, say so in the report, store headlines/metadata and scores only, pin the model revision.** Blocks: T-111.

### D-13 Multi-day horizons
The PRD requires "multi-day" but names none. **Recommendation (mine): h = 5 and h = 21 sessions (one trading week, about one month)**, forward log return from the close of *t* to the close of *t+h*, purge/embargo of *h−1* sessions before every boundary, non-overlapping evaluation samples every *h* sessions for inference. Blocks: labels, purge.

### D-16 70/15/15 vs the agreed target-date split
PRD §9.4 says 70/15/15; `DECISIONS.md` agreed a target-date split (≈ 74 / 22 / 4.7 % of rows). **Recommendation (mine): keep the agreed split and state the deviation and reason in the report.**

### D-18 Transaction costs
Not defined. **Recommendation (mine): a stated round-trip assumption (brokerage, STT, exchange charges, GST, stamp duty, slippage) set from a published broker schedule before any backtest, with a 2× sensitivity.** Needs your choice of broker schedule. Blocks: backtest.

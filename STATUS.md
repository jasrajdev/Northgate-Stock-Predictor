# Current Status

Updated: 2026-11-13

## Project state
- Repository: private GitHub repository; default branch `main`.
- Stage: market-data ingestion, feature engineering, and first next-session supervised dataset generation have been run successfully on the user's Mac.
- Environment: MacBook Air M4, user-reported 16 GB unified memory; project virtual environment `.venv/`. Latest terminal session used Python 3.14 according to the earlier installation output (the older Python 3.12.15 note was stale).
- Declared dependencies: NumPy, pandas, yfinance; pytest for development.
- Existing code: package/data-module placeholders, a market-data scaffold, and a project-structure test.
- Verified user-reported local data: 29,484 market-panel rows across 10 provisional equities plus NIFTY 50, and a 29,484-row feature panel with 24 engineered features. Per-ticker volume anomaly handling has been added. The next-day modelling dataset was generated locally: 29,473 labelled rows across 11 instruments; 11 final per-ticker rows were removed because no next-session label exists. User-provided checks: zero duplicate ticker/date keys, all target dates after feature dates, zero missing target values, and zero non-positive target adjusted closes.
- No models have been trained; no backtest, dashboard, or performance result has been produced. A target-date-based chronological split script has been added to GitHub and run locally. User verified all three CSV outputs and the JSON report; 29,473 rows are partitioned across 11 instruments (21,708 train; 6,379 validation; 1,386 test), with all six script checks passing.
- The original PRD is referenced by the project notes but is not present as a standalone file in the current GitHub repository tree reviewed on this date. Keep its requirements visible until it is added or otherwise made available as a durable project file.

## Confirmed project direction
- Research focus: Indian equities.
- NIFTY 50 is a candidate universe and benchmark family, not a final stock-selection decision.
- Build a reproducible research and decision-support system, not a live brokerage execution bot.
- Preserve chronological out-of-sample testing, point-in-time information, simple baselines, transaction-cost awareness, and honest reporting.
- The PRD's requested scope remains the reference scope: 8–15 liquid equities plus a benchmark, 8–10 years of data, the specified model comparisons, sentiment/news comparison, portfolio optimisation, dashboard, and report. Any scope reduction or expansion must be explicit rather than silently assumed.
- Recommendation principle confirmed 2026-11-12: no daily trade is required. The system must be allowed to recommend no new trade across the whole portfolio, must apply pre-defined criteria consistently, and must not force a sale/rotation simply because another asset has a higher forecast. See `DECISIONS.md`.

## Not yet decided
- Whether the PRD's 8–15 stocks are only the baseline research universe or also the eventual prediction/coverage limit.
- Whether training on a broader multi-company panel can generalise to additional unseen Indian equities; this requires a fair out-of-sample experiment and is not assumed.
- Exact stocks, benchmark series, historical membership method, and data providers.
- Multi-day forecast horizon(s), recommendation thresholds, uncertainty/abstention rules, trade entry/exit convention, and what constitutes a successful BUY.
- Whether the practical 70% BUY-win-rate aspiration previously discussed should remain an evaluation objective; it is not a verified result or a PRD acceptance criterion.
- News sources, coverage, API provider(s), event taxonomy, model approach, and workflow scheduler/orchestrator.
- Final model set beyond the PRD comparison requirements, and any scope trade-offs needed for the recorded 15 November 2026 deadline.

## Latest research progress
- Fieberg et al. (2023) full-paper extraction reviewed. Its useful findings and limitations have been consolidated into the single rolling document `docs/RESEARCH_ROADMAP.md`; no separate paper-summary file is maintained.
- The paper studies monthly pooled cross-sectional returns across a broad European universe, not daily price forecasting or a small 8–15-stock universe. It does not establish transferability to Indian equities.
- The rolling research synthesis now compares Gu–Kelly–Xiu and Fieberg and identifies the PRD's daily forward-price task versus the papers' monthly return-prediction task as a key unresolved mismatch.

## Next action
Continue EDA and prepare macro/market and timestamped news/sentiment data, aligning each item to its actual release/publication time. Define the unspecified multi-day horizons before creating those labels. Keep the final six-month test set untouched until model selection is frozen.

## Progress rule
Update this file only for verified progress and decisions the user has confirmed. Keep provisional brainstorming in the conversation; do not turn every idea into a repository entry. After any repository edit, fetch the saved file and verify its contents.


## Hardware and execution plan (2026-11-12)
- User reports an Apple M4 MacBook Air with 16 GB unified memory. Use it for data preparation, EDA and classical ML; Apple MPS may accelerate supported neural-network operations.
- Friend's HP Victus reportedly has 6 GB VRAM, but exact GPU model is unknown. Confirm GPU model and CUDA support before relying on it.
- A full PRD run (four classical models, four deep architectures, sentiment integration, portfolio/backtesting, dashboard and report) in one day is not guaranteed. Prioritise reproducible data, baseline and a defensible subset; report anything unfinished honestly.


## Latest verified milestone — 2026-11-12
- User ran `git pull origin main` successfully and executed `python scripts/build_next_day_dataset.py`.
- Output: 29,484 input rows; 29,473 rows with next-session labels; 11 rows removed (one final row per each of 11 tickers); 11 tickers.
- Validation output: duplicate ticker/feature-date keys = 0; target date after feature date = True for all rows; missing target values = 0; non-positive target adjusted close = 0.
- Local output paths reported by user: `data/processed/modeling_dataset_next_day.csv` and `reports/data_quality/next_day_dataset_report.json`.
- These results are user-provided terminal output; files were not independently inspected in this session. No model training has started.
- Next datasets: macro/market context and timestamped news/sentiment. Sentiment must be compared against the price/volume baseline on the same chronological dates; no incremental value is assumed.


## 2026-11-13 — Chronological split plan agreed; script added
- User approved a chronological first-pass split: training target dates through 2023-12-31, validation target dates after that and before the final six-calendar-month test window, and an untouched final six-month test window.
- Added `scripts/create_chronological_splits.py`. It calculates the test cutoff from the latest target date, assigns rows by `target_date_t1`, writes train/validation/test CSVs and a JSON report, checks chronological separation and duplicate keys, and identifies all `target_*` columns as forbidden model inputs.
- Current user-reported latest target date is 2026-11-09, implying a calendar cutoff of 2026-05-09. The exact first test trading date and partition counts must be confirmed by running the script locally.
- Script has been fetched back from GitHub and its saved contents verified. It has not yet been run locally; no model training has occurred.


### 2026-11-13 — Chronological partitions generated and verified locally
- User ran `python scripts/create_chronological_splits.py` successfully on the Mac.
- Actual partitions: training 21,708 rows (target dates 2016-01-04 to 2023-12-29); validation 6,379 rows (2024-01-01 to 2026-05-08); final test 1,386 rows (2026-05-11 to 2026-11-09). Each partition contains 11 tickers and 39 columns.
- All six script checks passed: no duplicate ticker/feature-date keys; all target dates after feature dates; train before validation; validation before test; all rows assigned exactly once; target columns excluded from candidate feature columns.
- User separately inspected all three CSV files and confirmed their shapes, ticker counts, target columns and date ranges. The JSON report exists locally at `reports/data_quality/chronological_split_report.json`.
- Feature-date ranges overlap at partition boundaries by design: rows are assigned according to when their target becomes known. For example, the first validation target on 2024-01-01 uses a feature date of 2023-12-29; the first test target on 2026-05-11 uses a feature date of 2026-05-08. This is correct for next-session forecasting.
- Split CSVs and JSON report are local generated outputs; they have not been committed to GitHub. No models have been trained.


## 2026-11-13 — CPI release workbook extraction completed
- Inspected all 18 Project-backed MoSPI monthly Excel annexure workbooks from July 2024 through December 2025; no additional upload was required.
- Added `data/external/cpi_mospi_2012_release_vintages_2024-07_to_2025-12.csv` (108 rows): monthly rural/urban/combined headline index values, provisional current-month inflation, and preceding-month final index observations.
- Added `data/external/cpi_mospi_2012_historical_table_snapshots_2024-07_to_2025-12.csv` (3,990 rows): historical CPI index and YoY inflation table snapshots across 14 supplied release workbooks.
- Observed revisions in the supplied provisional-to-final comparison: combined index changed in 4 of 17 matched months (max absolute change 0.2 points); rural in 1/17 (0.1); urban in 5/17 (0.4). Preserve vintage records rather than overwriting them.
- Inspected the separate `cpi_33.xlsx`: 31,460 rows, 22 months, base 2024; 2025 inflation is null throughout. It has no release timestamps or vintage identifiers and is not an as-published 2025 archive.
- GitHub CSV files were fetched back and row-count verified. `docs/DATA_RESEARCH.md` now documents extraction method, coverage, revision checks and limitations.
- CPI is not yet ready to merge into market features: actual official release dates/times must be mapped, and an as-of join must assign each release to the next eligible NSE session. No CPI model feature has been built or backtested yet.

## Next action
Map each supplied CPI workbook to its official MoSPI release date/time, verify the release-time regime and next eligible NSE session, then construct a point-in-time CPI feature table. Keep the 2024-base snapshot separate from the contemporaneously available 2012-base series.


### CPI publication-time and market-availability mapping
- Added `data/external/cpi_mospi_2012_release_availability_map_2024-07_to_2025-12.csv` (18 rows), with reference month, release date/time, evidence status, next eligible NSE session and source URL.
- 17 rows have direct official PDF support. April 2025 reference-month CPI remains scheduled-only (12 May 2025 cited as the expected date by the previous release); its own PDF must be found before the timestamp is considered verified.
- All verified release times are after the 15:30 NSE cash close. Next-session mapping accounts for weekends and official NSE equity-market holidays.
- GitHub copy fetched back and verified at 18 data rows. Details and sources are in `docs/DATA_RESEARCH.md`.

**Current CPI status:** extraction and release/session mapping are documented; not yet integrated into market features. Next: locate/verify April 2025's PDF, join the availability map to the two vintage datasets, create a leakage-safe as-of feature table, then validate null handling and chronological availability.


### 2026-11-13 — CPI vintage source and availability pipeline
- User supplied the April 2025 MoSPI Excel annexure workbook. Verified it contains Annex-VI/VII and explicitly marks April 2025 CPI index 192.6 and YoY inflation 3.16% as provisional; March 2025 is final.
- Verified the corresponding official April 2025 CPI release was actually published 13 May 2025 at 16:00 IST, not the previously expected 12 May. It becomes available for this project's close-based NSE features from the next eligible session, 14 May 2025.
- Inspected all 18 monthly CPI workbooks (July 2024–December 2025). Annex-VI/VII cumulative historical time-series snapshots are available in 14 releases (November 2024–December 2025), yielding 3,990 index/inflation vintage rows. Provisional markers are preserved; duplicate vintage keys = 0.
- Added `data/external/cpi_release_availability_map_2012base.csv` and `scripts/build_cpi_vintages.py`. The script is saved and fetched back from GitHub; local execution against the complete input folder remains pending.
- The extracted vintage CSV and original workbook-derived snapshots are present in the working environment, but the new large generated vintage CSV has not yet been committed to GitHub through the repository connector. Do not claim it is durably saved until verified in the repository.
- No daily NSE-aligned feature table has been built yet. The deterministic as-of join remains the next data-engineering step; it must use the next eligible NSE session after actual release and retain vintage status.

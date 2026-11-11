# Current Status

Updated: 2026-11-12 (late session)

## Project state
- Repository: private GitHub repository; default branch `main`.
- Stage: market-data ingestion, feature engineering, and first next-session supervised dataset generation have been run successfully on the user's Mac.
- Environment: MacBook Air M4, user-reported 16 GB unified memory; project virtual environment `.venv/`. Latest terminal session used Python 3.14 according to the earlier installation output (the older Python 3.12.15 note was stale).
- Declared dependencies: NumPy, pandas, yfinance; pytest for development.
- Existing code: package/data-module placeholders, a market-data scaffold, and a project-structure test.
- Verified user-reported local data: 29,484 market-panel rows across 10 provisional equities plus NIFTY 50, and a 29,484-row feature panel with 24 engineered features. Per-ticker volume anomaly handling has been added. The next-day modelling dataset was generated locally: 29,473 labelled rows across 11 instruments; 11 final per-ticker rows were removed because no next-session label exists. User-provided checks: zero duplicate ticker/date keys, all target dates after feature dates, zero missing target values, and zero non-positive target adjusted closes.
- No models have been trained; no backtest, dashboard, or performance result has been produced.
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
Prepare and validate the PRD's macro/market dataset and timestamped news/sentiment dataset; align all releases/stories to when they became available. Define the unspecified multi-day horizons before creating those labels. Continue with EDA and baseline modelling after the dataset inputs are aligned.

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

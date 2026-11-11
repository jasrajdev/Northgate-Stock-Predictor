# Current Status

Updated: 2026-11-12

## Project state
- Repository: private GitHub repository; default branch `main`.
- Stage: market-data ingestion and first-pass feature engineering are implemented; next-session supervised dataset builder has been added but not yet run on the user's Mac.
- Environment recorded: Mac, VS Code, Python 3.12.15 virtual environment at `.venv/`.
- Declared dependencies: NumPy, pandas, yfinance; pytest for development.
- Existing code: package/data-module placeholders, a market-data scaffold, and a project-structure test.
- Verified user-reported local data: 29,484 market-panel rows across 10 provisional equities plus NIFTY 50, and a 29,484-row feature panel with 24 engineered features. Per-ticker volume anomaly handling has been added. The next-day target builder is in GitHub but its output has not yet been generated/verified locally.
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
Run `scripts/build_next_day_dataset.py` on the user's Mac and inspect its validation report. Then prepare the PRD's macro/market dataset and timestamped news/sentiment dataset; agree multi-day forecast horizons before adding those labels. Confirm the friend's exact GPU before deciding where deep-learning training will run.

## Progress rule
Update this file only for verified progress and decisions the user has confirmed. Keep provisional brainstorming in the conversation; do not turn every idea into a repository entry. After any repository edit, fetch the saved file and verify its contents.


## Hardware and execution plan (2026-11-12)
- User reports an Apple M4 MacBook Air with 16 GB unified memory. Use it for data preparation, EDA and classical ML; Apple MPS may accelerate supported neural-network operations.
- Friend's HP Victus reportedly has 6 GB VRAM, but exact GPU model is unknown. Confirm GPU model and CUDA support before relying on it.
- A full PRD run (four classical models, four deep architectures, sentiment integration, portfolio/backtesting, dashboard and report) in one day is not guaranteed. Prioritise reproducible data, baseline and a defensible subset; report anything unfinished honestly.

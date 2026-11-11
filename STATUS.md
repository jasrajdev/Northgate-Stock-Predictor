# Current Status

Updated: 2026-11-12

## Project state
- Repository: private GitHub repository; default branch `main`.
- Stage: initial Python project scaffold exists. Research and architecture planning are in progress; implementation has not advanced beyond the scaffold.
- Environment recorded: Mac, VS Code, Python 3.12.15 virtual environment at `.venv/`.
- Declared dependencies: NumPy, pandas, yfinance; pytest for development.
- Existing code: package/data-module placeholders, a market-data scaffold, and a project-structure test.
- No market dataset has been downloaded; no models have been trained; no backtest, dashboard, or performance result has been produced.
- The original PRD is referenced by the project notes but is not present as a standalone file in the current GitHub repository tree reviewed on this date. Keep its requirements visible until it is added or otherwise made available as a durable project file.

## Confirmed project direction
- Research focus: Indian equities.
- NIFTY 50 is a candidate universe and benchmark family, not a final stock-selection decision.
- Build a reproducible research and decision-support system, not a live brokerage execution bot.
- Preserve chronological out-of-sample testing, point-in-time information, simple baselines, transaction-cost awareness, and honest reporting.
- The PRD's requested scope remains the reference scope: 8–15 liquid equities plus a benchmark, 8–10 years of data, the specified model comparisons, sentiment/news comparison, portfolio optimisation, dashboard, and report. Any scope reduction must be explicit rather than silently assumed.

## Not yet decided
- Exact stocks, benchmark series, historical membership method, and data providers.
- Forecast target(s), prediction horizon(s), recommendation rules, trade entry/exit convention, and what constitutes a successful BUY.
- Whether the practical 70% BUY-win-rate aspiration previously discussed should remain an evaluation objective; it is not a verified result or a PRD acceptance criterion.
- News sources, coverage, API provider(s), event taxonomy, model approach, and workflow scheduler/orchestrator.
- Final model set beyond the PRD comparison requirements, and any scope trade-offs needed for the recorded 15 November 2026 deadline.

## Latest research progress
- Fieberg et al. (2023) full paper reviewed using the uploaded source-only extraction instructions; detailed extraction is saved at `docs/FIEBERG_2023_RESEARCH_EXTRACTION.md`.
- The paper studies monthly pooled cross-sectional returns across a broad European universe, not daily price forecasting or a small 8–15-stock universe. It does not establish transferability to Indian equities.
- `docs/RESEARCH_ROADMAP.md` now records the review and prioritises cross-paper synthesis.

## Next action
Synthesize the evidence across the reviewed papers, keeping India transferability and the PRD's daily forecasting task unresolved; then agree the evaluation contract and run a small data-source feasibility pilot before bulk collection or model training.

## Progress rule
Update this file only for verified progress and decisions the user has confirmed. Keep provisional brainstorming in the conversation; do not turn every idea into a repository entry. After any repository edit, fetch the saved file and verify its contents.

# Current Status

- Project repository created: private GitHub repo, default branch `main`.
- Stage: initial project structure created; research-led dataset design is the next task before market-data ingestion is implemented.
- Deadline: 15 November 2026.
- Working style: learn by building; concise, beginner-friendly explanations; explain unfamiliar terms in brackets once.
- Environment: Mac + VS Code + GitHub; Python 3.12.15 virtual environment at `.venv/`; `.gitignore` excludes local environments and caches.
- Initial dependencies declared: NumPy, pandas, yfinance; pytest in development requirements.
- Added `src/northgate/`, a data module scaffold, tests, and placeholder directories for raw/processed data, notebooks, and reports.
- Market focus: Indian equities. Candidate starting universe is NIFTY 50, but final stock subset, benchmark series, prediction target/horizon, and source remain undecided.
- Current priority: research price/volume data and establish a valid backtesting baseline before the news/event-analysis phase.
- Created `docs/DATA_RESEARCH.md` with candidate data fields, official source links, research papers, stock-universe guidance, and questions to extract from papers.
- Important research caution: the 2022 NIFTY 50 forecasting paper describes an 80/20 split and K-fold validation within training. Verify that its validation preserves time order before adopting its method; random K-fold can leak future information in time series.
- NSE All Reports is a candidate for daily market files; NSE separately advertises paid historical data, so long-range free coverage must be verified.
- News/event analysis remains preserved as phase 2: company news, policy, RBI/macroeconomics, global events, market-wide and sector events. These are hypotheses, not proven predictors.
- No stock data has been downloaded, no models have been trained, and no performance claims/results exist.
- Next: finish reading the 2022 NIFTY 50 paper, especially its target, data split, and baseline; then compare its setup with the PRD and choose a small, documented initial universe.

## Session update rule
After each meaningful work session, record completed work, tests/results, decisions, new ideas, blockers, and the single next action. Update this file and verify the saved contents.

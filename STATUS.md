# Current Status

- Project repository created: private GitHub repo, default branch `main`.
- Stage: initial project structure created; research-led dataset design is the next task before market-data ingestion is implemented.
- Deadline: 15 November 2026.
- Working style: learn by building; concise, beginner-friendly explanations; explain unfamiliar terms in brackets once.
- Environment: Mac + VS Code + GitHub; Python 3.12.15 virtual environment at `.venv/`; `.gitignore` excludes local environments and caches.
- Initial dependencies declared: NumPy, pandas, yfinance; pytest in development requirements.
- Added `src/northgate/`, a data module scaffold, tests, and placeholder directories for raw/processed data, notebooks, and reports.
- Market focus: user chose Indian equities on 2026-10-19. Specific stocks, benchmark, prediction target/horizon, and data source remain undecided.
- Current priority: research what price/volume data to collect and establish a credible backtesting baseline before the news/event-analysis phase.
- Created `docs/DATA_RESEARCH.md` with candidate data fields, official source links, research papers, questions to extract from papers, and safeguards.
- NSE All Reports is a candidate for daily market files; NSE separately advertises paid historical data, so long-range free coverage must be verified before choosing a source.
- RBI DBIE is a candidate for a later macroeconomic-data phase.
- News/event analysis remains preserved as phase 2: company news, policy, RBI/macroeconomics, global events, market-wide and sector events. These are hypotheses, not proven predictors.
- No stock data has been downloaded, no models have been trained, and no performance claims/results exist.
- Next: read the NIFTY 50 prediction paper and extract target/horizon, raw fields, split method, baselines, data source, and limitations. Then compare with PRD requirements before fixing our own dataset.

## Session update rule
After each meaningful work session, record completed work, tests/results, decisions, new ideas, blockers, and the single next action. Update this file and verify the saved contents.

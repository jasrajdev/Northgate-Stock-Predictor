# Current Status

- Project repository created: private GitHub repo, default branch `main`.
- Stage: initial project structure created; research-led dataset design is the next task before market-data ingestion is implemented.
- Deadline: 15 November 2026.
- Working style: learn by building; concise, beginner-friendly explanations; explain unfamiliar terms in brackets once.
- Environment: Mac + VS Code + GitHub; Python 3.12.15 virtual environment at `.venv/`; `.gitignore` excludes local environments and caches.
- Initial dependencies declared: NumPy, pandas, yfinance; pytest in development requirements.
- Added `src/northgate/`, a data module scaffold, tests, and placeholder directories for raw/processed data, notebooks, and reports.
- Market focus: user chose Indian equities on 2026-10-19. Specific stocks, benchmark, prediction target/horizon, macro series, and news sources remain undecided.
- New research direction: investigate company news plus government/regulatory policy, RBI/macroeconomic releases, global events, market-wide information, and price/volume features. These are candidate inputs, not proven predictors.
- Research leads identified: Nifty 50 news-topic paper (arXiv:2412.06794), NIFTY Financial News Headlines dataset paper (arXiv:2405.09747), Tetlock (2007), and FinBERT paper (arXiv:1908.10063). Not all have been fully reviewed.
- Official source candidates to evaluate: NSE daily reports/bhavcopy and RBI Database on Indian Economy (DBIE); news-source access and historical timestamp coverage are unresolved.
- No stock data has been downloaded, no models have been trained, and no performance claims/results exist.
- Next: read the India/Nifty news-topic paper and the NIFTY dataset paper, extract their data choices and limitations, then decide the first target/horizon and source shortlist before downloading data.

## Session update rule
After each meaningful work session, record completed work, tests/results, decisions, new ideas, blockers, and the single next action. Update this file and verify the saved contents.

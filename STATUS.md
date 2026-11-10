# Current Status

- Project repository created: private GitHub repo, default branch `main`.
- Stage: initial project structure exists; moving from research planning to implementation planning.
- Deadline: 15 November 2026.
- Working style: learn by building; concise, beginner-friendly explanations; explain unfamiliar terms in brackets once.
- Environment: Mac + VS Code + GitHub; Python 3.12.15 virtual environment at `.venv/`; `.gitignore` excludes local environments and caches.
- Initial dependencies declared: NumPy, pandas, yfinance; pytest in development requirements.
- Added `src/northgate/`, a data module scaffold, tests, and placeholder directories for raw/processed data, notebooks, and reports.
- Market focus: Indian equities. NIFTY 50 is a candidate universe; final 8–15 stocks and benchmark series still need a reproducible selection rule.
- User's additional practical objective: aim for at least 70% profitable BUY recommendations over a five-trading-session holding period. This is a research target, not a guaranteed result; evaluate net returns, average win/loss, profit factor, drawdown, Sharpe, trade count, and uncertainty too.
- PRD acceptance criteria remain mandatory: best forecaster beats naive random walk on MAE and directional accuracy; optimised portfolio beats equal-weight baseline on out-of-sample Sharpe; four ML + four DL models; sentiment comparison; MPT; dashboard; report.
- Read the original PRD and the user's uploaded review of the 2022 NIFTY 50 paper. Findings and caveats are preserved in `docs/RESEARCH_PAPER_REVIEW.md`.
- Added `docs/IMPLEMENTATION_PLAN.md` with staged implementation, separate forecasting/recommendation/portfolio evaluations, proposed trade convention, leakage safeguards, and timeline risk.
- Proposed but not yet confirmed trade convention: signal after close, enter next session open, exit fifth session close. Need agree this and transaction-cost assumptions before backtesting.
- Research paper caveats: index forecasting is not portfolio profitability; reported model ranking varies by metric; K-fold chronology and exact target construction need scrutiny; StandardScaler must be fitted on training data only.
- Current priority: agree the evaluation contract, then run a small India-data source feasibility pilot. Do not bulk-download data or train models yet.
- No stock data has been downloaded, no models have been trained, and no performance claims/results exist.
- Timeline risk: PRD planned four weeks at 25–30 hours/week; recorded deadline is 15 November 2026. Prioritise a correct reproducible core and disclose incomplete scope.

## Session update rule
After each meaningful work session, record completed work, tests/results, decisions, new ideas, blockers, and the single next action. Update this file and verify the saved contents.
- Strategy refinement (2026-11-11): five sessions is now a proposed maximum holding period, not a mandatory exit date. Explore return-based exits using a take-profit barrier, stop-loss/risk exit, and max-five-session time exit. No fixed 5%/10% target has been chosen.
- New research direction: estimate empirical 1–5 session return/volatility distributions, compare fixed vs volatility-scaled exit barriers, include costs, and select rules on chronological validation only. See `docs/IMPLEMENTATION_PLAN.md`.
- Evidence reviewed: academic studies show stop-loss/trailing-stop effects depend on return dynamics and transaction costs; there is no universal optimal threshold. See cited studies in implementation plan and ideas backlog.

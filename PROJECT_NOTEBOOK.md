# Project Notebook

## Research question
Can machine learning discover a useful signal in stock-market data that improves investment decisions out of sample?

## Required scope from Northgate PRD
- 8–15 liquid large-cap equities plus a market benchmark; roughly 8–10 years of daily OHLCV and adjusted-close data, relevant macro series, and timestamped financial news.
- EDA and finance math; compare 4 classical ML models (Linear/Ridge, Random Forest, XGBoost, SVR) and 4 deep-learning models (LSTM, GRU, BiLSTM, Transformer).
- Test FinBERT/VADER sentiment impact; mean-variance portfolio optimization; backtesting, risk metrics, recommendation logic, and a 7-panel Streamlit dashboard.
- Deliver reproducible code, comparisons, dashboard, and a 10–15 page report. Check the original PRD for exact requirements before finalizing.

## Current research direction — 2026-10-20
- Market focus: Indian equities.
- Current priority is price/volume data, target/horizon selection, and a valid backtesting baseline. News/event analysis is phase 2, not abandoned.
- User wants research papers and source documentation to guide data choices rather than selecting features arbitrarily.
- Specific stock universe, benchmark, prediction target/horizon, and final data source remain open.
- Candidate price fields: date, open, high, low, close, adjusted close or documented adjusted series, volume, instrument identifier.
- Candidate derived features: returns, rolling volatility, moving averages, volume changes. Must be calculated without using future data.
- Source candidates: NSE All Reports for daily files; check NSE historical-data terms/coverage because NSE also advertises paid historical subscriptions. RBI DBIE is a possible later source for macro series.
- A 2022 NIFTY 50 ML paper is a research lead for typical data fields and evaluation design; review its split methodology and limitations rather than copying its choices.
- News/event research leads remain in `docs/DATA_RESEARCH.md` and `IDEAS_BACKLOG.md`. Candidate topics include company announcements, government policy, RBI/economic releases, global/commodity events, and market-wide/sector news.
- Event/news co-occurrence cannot prove causation. Build a simple baseline before considering multi-agent complexity.

## Non-negotiable research safeguards
- Split data by time, never randomly across dates.
- At each prediction date, use only information that would actually have been available then. Align after-close news to the next trading session.
- Compare forecasts with a naive last-value/random-walk baseline; compare portfolios with equal weight and a benchmark.
- Include transaction costs/slippage where feasible; disclose limitations. A model losing to a baseline is a valid finding.
- Freeze choices before final testing where possible; do not tune against the test period.
- This is research/decision support, not live brokerage execution or a guarantee of returns.

## Build philosophy
Build in small tested steps. Explain what each step achieves and why. Prefer reproducibility, simple baselines, and transparent results over complexity for its own sake.

## Core concept
Historical backtesting is like replaying the past: on every simulated date, the system must know only what an investor could have known on that date. Seeing future information is look-ahead bias/data leakage.

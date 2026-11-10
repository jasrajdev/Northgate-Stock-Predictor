# Project Notebook

## Research question
Can machine learning discover a useful signal in Indian stock-market data that improves investment decisions out of sample?

## Required scope from Northgate PRD
- 8–15 liquid large-cap equities plus a broad market benchmark; at least 8–10 years of daily OHLCV and adjusted-close data, relevant macro series, and timestamped financial news.
- EDA and finance math; compare 4 classical ML models (Linear/Ridge, Random Forest, XGBoost, SVR) and 4 deep-learning models (LSTM, GRU, BiLSTM, Transformer).
- Test FinBERT/VADER sentiment impact; mean-variance portfolio optimization; backtesting, risk metrics, recommendation logic, and a 7-panel Streamlit dashboard.
- Deliver reproducible code, comparisons, dashboard, and a 10–15 page report. See original PRD for exact requirements.

## User-defined practical success objective — 2026-11-09
- Aim for at least 70% of BUY recommendations to result in positive net returns over a five-trading-session holding period.
- This is a target to test, not a promise or established performance.
- A 70% win rate alone does not prove profitability: measure average win/loss, net return after costs, profit factor, drawdown, Sharpe, trade count, and uncertainty.
- Do not equate a regression forecast with a calibrated probability of success.

## Two distinct evaluation layers
1. Forecasting: compare all eight models on identical held-out dates; PRD requires beating naive random-walk on MAE and directional accuracy.
2. Strategy/portfolio: simulate BUY/HOLD/SELL and allocations; PRD requires optimised portfolio out-of-sample Sharpe to exceed equal-weight baseline. Also compare broad-market benchmark.
Do not use model RMSE alone as evidence of profitable trading.

## Current implementation direction — 2026-11-09
- Market focus: Indian equities; NIFTY 50 is a candidate starting universe. PRD final universe must be 8–15 equities, not 20–30.
- News/event research is phase 2 after a working price/volume baseline; preserve candidate news categories in `IDEAS_BACKLOG.md`.
- Read user's 2022 NIFTY 50 paper briefing; detailed notes and caveats are in `docs/RESEARCH_PAPER_REVIEW.md`.
- Stepwise implementation plan is in `docs/IMPLEMENTATION_PLAN.md`.
- Proposed trade convention (not final): signal after close on t, enter at t+1 open, exit at t+5 close.
- Need source feasibility test before full data download; yfinance is in PRD reference code but Indian coverage, corporate-action adjustments, and long-history reliability must be checked. NSE official files/historical data are another candidate; historical access may have costs.
- Historical index membership is important: selecting only current NIFTY 50 constituents for past years can create survivorship bias. Use point-in-time membership if accessible; otherwise disclose limitation.
- Avoid blindly forward-filling missing stock prices; inspect gaps and retain audit logs. Never back-fill.
- Do not train all eight models until data, target, split protocol, and baseline are tested.

## Non-negotiable research safeguards
- Split data by time, never randomly across dates.
- At each prediction date, use only information that would actually have been available then. Align after-close news to the next trading session.
- Fit scalers on training data only; transform validation/test using training-fitted parameters.
- For five-session forward outcomes, purge overlapping label horizons at split boundaries to prevent shared future outcome periods crossing folds.
- Compare forecasts with naive last-value/random-walk baseline; compare portfolios with equal weight and benchmark.
- Include transaction costs/slippage where feasible; disclose limitations. A model losing to a baseline is a valid finding.
- Freeze choices before final testing; do not tune against the test period.
- This is research/decision support, not live brokerage execution or a guarantee of returns.

## Build philosophy
Build in small tested steps. Explain what each step achieves and why. Prefer reproducibility, simple baselines, and transparent results over complexity for its own sake.

## Core concept
Historical backtesting is like replaying the past: on every simulated date, the system must know only what an investor could have known on that date. Seeing future information is look-ahead bias/data leakage.
## Return-based strategy refinement — 2026-11-11
- Five sessions is a maximum holding period, not a compulsory day-five exit. User wants exits based on a sensible return opportunity and risk, not an arbitrary fixed holding duration.
- No fixed 5% or 10% target selected. First measure Indian equity 1–5 session return and volatility distributions, then compare candidate take-profit/stop-loss rules on chronological validation data.
- Candidate structure: take-profit barrier, stop-loss/risk exit, and maximum-five-session exit. Compare fixed percentage barriers with volatility-scaled barriers (e.g. ATR); treat these as hypotheses.
- Tight exits may create turnover and transaction costs; include realistic charges/slippage. If daily OHLC suggests both barriers were crossed in one candle, order is unknown; use intraday data or conservative adverse-first handling.
- A 70% win rate remains a target, not the sole optimisation objective. Also measure net expectancy, average win/loss, profit factor, drawdown, Sharpe, turnover, trade count and uncertainty.
- Broader universe than the PRD's 8–15 may be explored if reliable historical data supports it, but expand in stages and address survivorship/sector correlation. More tickers are not automatically better.
- Models should be tested progressively: naive baseline → simple linear/logistic → tree-based → one sequence model; add other PRD architectures if evidence/time justifies or comparison is required. Do not train all at once.

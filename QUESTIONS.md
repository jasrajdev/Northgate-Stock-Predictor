# Open Questions

Resolve these through research or implementation; record answers here.

## Immediate evaluation contract
- Confirm trade timing: proposed signal after close on day t, enter at next session open, exit at close of fifth session (t+5). Is this the intended five-session holding period?
- Define exactly what counts as a BUY and a winning trade: positive net return after brokerage, taxes/fees, and slippage?
- What transaction-cost/slippage assumptions can be documented for Indian cash equities?
- How should simultaneous BUY signals share capital? Maximum number of holdings, per-stock cap, sector cap, and treatment of overlapping trades?
- Is the 70% win-rate target an aspirational validation objective, with final test results reported honestly even if below target? (Recommended.)
- How many completed trades are enough to make the win-rate estimate meaningful? Report confidence intervals and sample count.

## First-phase data and modelling
- Which 8–15 Indian equities and benchmark best fit the PRD, with reproducible selection rules and historical membership?
- Which source provides 8–10 years of daily OHLCV and corporate-action-adjusted prices at acceptable cost and with clear terms?
- Can yfinance provide reliable Indian equity data and adjusted OHLC for the chosen universe? Compare with NSE historical files/terms.
- Which target is primary for the PRD's forecast requirement: next-day and multi-day forward closing price/return, and how will this coexist with the five-session trade outcome?
- What chronological train/validation/test periods and walk-forward folds will be used?
- How will overlapping five-session labels be purged at split boundaries?
- How do we account for survivorship bias if point-in-time NIFTY constituent history is unavailable?

## Later phase: macro/news/events
- Which reliable source will provide Indian macroeconomic series and timestamped financial news?
- Which event/topic categories add value beyond price/volume?
- How will publication time, after-market news, revised economic data, duplicate stories, and historical availability be handled?

## Delivery
- Which local Python/deep-learning setup is practical on the available Mac, and when should Colab be used?
- What can be completed to a correct standard by the 15 November 2026 deadline, and what must be explicitly deferred?

## Return-based strategy design (added 2026-11-11)
- What is a realistic distribution of Indian stock returns over 1–5 trading sessions, by stock/sector and volatility regime?
- How often do candidate profit targets (e.g. a grid of modest fixed percentages) get reached within five sessions, and what adverse movement occurs first?
- Should exits use fixed percentage targets/stops, volatility-scaled barriers (e.g. ATR multiples), a trailing stop, or a combination?
- What is the appropriate risk/reward and net expectancy after brokerage, statutory charges, spread and slippage?
- What should happen if both target and stop appear to be crossed in the same daily OHLC candle? Can intraday data resolve ordering, or should the backtest assume the adverse outcome?
- Should the model estimate expected forward return, probability of reaching a profit barrier before a stop barrier, or both?
- Which objective should drive threshold selection: net expectancy, risk-adjusted return, drawdown-constrained return, or a multi-metric rule? Win rate alone is insufficient.
- How do we reduce overfitting when trying many exit thresholds and model configurations?

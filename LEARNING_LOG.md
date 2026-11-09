# Learning Log

For each entry: concept, plain-language meaning, why it matters here, example/test, remaining confusion.

## Backtesting and leakage
- Meaning: backtesting simulates a strategy on historical dates; leakage happens when information from the future slips into a prediction.
- Why it matters: it can make a weak strategy look unrealistically successful.
- Rule: on every date, features and news must reflect only information available at that time.
- Status: foundational rule; apply to data preparation, feature engineering, model selection, and portfolio tests.

## Forecasting vs recommendation vs portfolio evaluation — 2026-11-09
- Forecasting evaluation: checks whether predicted values/directions match future outcomes (e.g. MAE and directional accuracy).
- Recommendation win rate: among BUY signals actually generated, what fraction have positive net returns over the chosen holding period?
- Portfolio evaluation: checks the combined capital-weighted holdings, including risk, costs, and benchmark-relative performance.
- Why it matters: a low forecast error does not automatically mean profitable trades; a high win rate does not automatically mean a profitable portfolio.
- Northgate's user-defined target: aim for 70% profitable BUY recommendations over five trading sessions; not a guarantee or a substitute for PRD metrics.
- Open: precise signal time, entry/exit prices, transaction costs, position sizing, and handling of overlapping trades.

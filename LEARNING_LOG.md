# Learning Log

## Backtesting and leakage
- Meaning: backtesting simulates decisions on historical dates; leakage occurs when information from the future enters a prediction.
- Why it matters: leakage can make a weak strategy look unrealistically successful.
- Rule: at each simulated decision time, use only information available by that time.
- Status: foundational rule for data preparation, features, model selection, and portfolio tests.

## Three different evaluation questions
- Forecasting: did predicted values or directions match later market outcomes?
- Recommendation evaluation: did BUY/HOLD/SELL decisions produce useful outcomes under a clearly defined trade convention?
- Portfolio evaluation: did the combined capital-weighted holdings perform well after costs and risk?
- Why it matters: a low forecast error or high BUY win rate does not automatically imply a profitable or robust portfolio.
- Status: evaluation layers are distinct; precise targets, horizons, and rules remain open.

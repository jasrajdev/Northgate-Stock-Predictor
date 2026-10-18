# Learning Log

For each entry: concept, plain-language meaning, why it matters here, example/test, remaining confusion.

## Backtesting and leakage
- Meaning: backtesting simulates a strategy on historical dates; leakage happens when information from the future slips into a prediction.
- Why it matters: it can make a weak strategy look unrealistically successful.
- Rule: on every date, features and news must reflect only information available at that time.
- Status: foundational rule; apply to data preparation, feature engineering, model selection, and portfolio tests.
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

## CPI release vintages and workbook audit — 2026-11-13

- A **reference month** is the month the CPI value describes; a **release vintage** is the version of the data available when MoSPI published a particular release. These must be stored separately to avoid using later revisions in historical simulations.
- The uploaded 18 MoSPI workbooks show cumulative CPI index and YoY tables beginning with the November 2024 release in this source set. Earlier July–October 2024 files contain only current/prior headline annexures.
- The cumulative tables are arranged as years in rows and months in columns. Annexure numbering changes across releases; parse by table title rather than sheet number.
- A first overlap check compared 281 repeated month/series keys across available workbook snapshots and found no differences at stored precision. This is a limited consistency check, not evidence that revisions never occur.
- The next engineering step is a tidy parser with release timestamp/vintage metadata and cross-checks against each workbook's provisional/final headline table. No normalized dataset has been generated yet.


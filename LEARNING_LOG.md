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

## CPI parser implementation pilot — 2026-11-13

- Added a reusable parser that detects cumulative CPI index and YoY tables by title, reshapes year/month cells into tidy monthly records, and preserves both the release reference month (vintage) and observation month.
- Tested against 18 uploaded workbooks: 3,948 records across 14 cumulative vintages; 2,078 index and 1,870 inflation records.
- Checks passed for unique vintage/observation/series keys and no future observation months relative to the release reference month.
- Exact publication timestamps remain blank rather than guessed. The pilot CSV is temporary and not yet a modelling input.
- Next: test the parser automatically, reconcile headline provisional/final values to cumulative endpoints, and attach verified publication timestamps before session alignment.

## Start modelling before optional feature enrichment — 2026-11-13

- The first supervised price/volume dataset and chronological splits are sufficient to start a baseline experiment. CPI and news/sentiment are important PRD components but do not need to block initial model training.
- A per-stock first benchmark avoids directly fitting one pooled raw-price target across companies with different nominal price scales. Pooled learning can be tested later as a separate experiment.
- Compare Ridge, Random Forest, SVR and XGBoost against the naive last-adjusted-close predictor on identical validation rows.
- Keep the final six-month test set unopened during model selection. No training metrics are available until the local script is run.



## MoSPI CPI OpenAPI specification — 2026-11-13

- User successfully retrieved the official CPI OpenAPI YAML using Python requests (HTTP 200). The endpoint is GET /api/cpi/getCPIData on api.mospi.gov.in; guest access is supported, but requests are rate-limited per IP.
- API covers base years 2010, 2012 and 2024. Filter sets differ by base year and group/item level. Filter codes should be discovered from the documented filter endpoint because invalid codes can return HTTP 200 with an empty result.
- Pagination is page 1-based with a maximum of 100 rows per page. viz_req=true asks for all matching rows. The OpenAPI's 2024 example is 1.445 million records, so bounded filters and hard limits are mandatory.
- The API specification does not document historical release vintages/as-of access. Current API rows must not be used as if they were the contemporaneous values known to a historical investor. Preserve the separate release-vintage annexure pipeline.
- No API observation rows were downloaded or merged during this research step.

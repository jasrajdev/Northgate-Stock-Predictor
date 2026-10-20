# Data Research Plan — India-First

Updated: 2026-10-20
Status: research leads identified; not yet a final dataset specification.

## Current focus
First build a reproducible price/volume dataset and backtesting baseline for Indian equities. News and broader event analysis are a later phase, but their research leads and hypotheses are preserved below.

## Stock universe / market choice
- Candidate starting universe: NIFTY 50 constituents. NSE describes it as a diversified 50-stock index and publishes its methodology and constituent list: https://www.nseindia.com/static/products-services/indices-nifty50-index
- Why this is a reasonable starting point: large, actively traded companies across sectors; the index is designed using explicit rules including liquidity. This is a research starting point, not proof that every historical constituent is easy to obtain.
- Do not assume today's NIFTY 50 membership was the membership 5–10 years ago. Using today's members for the entire past creates survivorship bias. If historical constituents are unavailable, document this as a limitation rather than pretending it is absent.
- Start with a smaller subset across sectors for pipeline development, then expand to the full 50 if data coverage and time allow. Final subset and selection rule remain undecided.
- Portfolio comparison should ideally use the NIFTY 50 Total Returns Index (TRI), because it includes dividends; plain price-index returns omit dividends. Verify the exact benchmark series and access terms before implementation.

## What to learn before choosing data
1. Define the prediction target: price level, next-session return/direction, or volatility. These are different tasks.
2. Define the horizon: how far ahead the forecast refers to (for example, the next trading session). Choose one primary target/horizon before modelling.
3. Select a benchmark and stock-selection rule. Avoid choosing stocks only because they are successful today; that creates survivorship bias.
4. Check historical coverage, field definitions, adjustment for splits/dividends, trading-calendar gaps, licensing, and download reproducibility.
5. Establish a simple baseline before adding many features.
6. Keep train/validation/test periods chronological and ensure every feature was available at the simulated prediction time.

## Initial core price/volume fields
For each trading date and instrument, investigate availability and definitions for:
- Date / trading session
- Open, High, Low, Close
- Adjusted close or a documented corporate-action-adjusted price series
- Volume
- Instrument identifier and exchange
Potential later derived features (calculated from historical data): returns, rolling volatility, moving averages, and volume changes. These are candidate features, not guaranteed predictors.

## Candidate sources to verify
- NSE All Reports: https://www.nseindia.com/all-reports
  - Official daily reports include market files such as the current CM-UDiFF Common Bhavcopy Final and full security bhavdata.
  - Important: NSE's separate paid End-of-Day/Historical Data subscription page exists. Do not assume all long-range official history is freely downloadable; verify coverage and terms before relying on it.
- NSE paid historical data information: https://www.nseindia.com/static/market-data/eod-historical-data-subscription
- RBI Database on Indian Economy: https://data.rbi.org.in/
  - Candidate source for macroeconomic and financial series in a later feature phase. Confirm series frequency, historical availability, release dates, revisions, and terms.
- Research paper: “Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques” (2022): https://doi.org/10.1080/08839514.2022.2111134
  - Studies NIFTY 50 index forecasting with RNN, LSTM, and CNN; the article abstract reports lower MSE for LSTM than the other two models.
  - The paper describes an 80/20 train/test split and K-fold cross-validation within training. Because this is time-series data, scrutinize whether folds preserve chronological order; ordinary random K-fold can leak future information. Do not copy its validation setup without checking.
  - Its described inputs include Date, Open, High, Low, Close, and Volume. Read the full methodology and limitations; an index forecast is not the same task as selecting individual stocks and constructing a portfolio.
- Research paper: “Understanding the Impact of News Articles on the Movement of Market Index: A Case on Nifty 50”: https://arxiv.org/abs/2412.06794
  - Later-phase lead for broad news topics, not only company headlines.
- Research paper/dataset: “NIFTY Financial News Headlines Dataset”: https://arxiv.org/abs/2405.09747
  - Later-phase lead for headline collection, filtering, deduplication, and timestamp alignment. Its actual market-data context may not directly match the Indian stock universe; check the paper before reusing methods.

## Questions to answer from each paper
- What exact prediction target and horizon did they use?
- Which instruments and date range?
- Which raw fields and derived features?
- What was the training/validation/test split?
- Was the split chronological, and was any future information able to leak in?
- What baseline did they compare against?
- Did they evaluate forecast error, directional accuracy, and/or portfolio returns after costs?
- Are the data source, timestamps, code, and dataset reproducible?
- What limitations do the authors acknowledge?

## News and event ideas to preserve for phase 2
Candidate groups: company announcements/earnings, government and regulatory policy, RBI and macroeconomic releases, global events (including commodities), market-wide flows, and sector-level events. A later pipeline could classify event type, affected company/sector, sentiment, source, timestamp, and duplicate status.
For unusually large price moves, an event-study tool could search for contemporaneous announcements as plausible explanations. Co-occurrence is not proof of causation. Do not build a complex multi-agent system or train a new language model before a simpler baseline demonstrates a need.

## Current recommendation
Research first, then start with the smallest useful dataset: daily price/volume history for a documented Indian universe plus a market benchmark. Finalize the exact ticker list, prediction target/horizon, and source only after reading at least one directly relevant paper and checking data coverage. Do not download the full dataset yet.

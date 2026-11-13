# PRD Requirements Reference — v1.0

Source: user-provided `Northgate Quantitative Research — AI Stock Prediction & Portfolio Optimization`, PRD v1.0 (30 pages). This file is a concise traceable requirements reference, not a replacement for the original brief.

## Core objective
Build an end-to-end Indian-equity decision-support research platform combining historical market data, macroeconomic indicators, financial-news sentiment, forecasting, portfolio optimisation, recommendations and an interactive Streamlit dashboard.

## Data requirements (PRD Sections 3–4)
- 8–15 liquid large-cap equities plus one broad-market benchmark.
- At least 8–10 years of daily OHLCV and adjusted-close data per equity.
- Market context: broad equity index; volatility index (PRD example: CBOE VIX); short-term rate (DGS3MO / policy rate); 10-year yield (DGS10); inflation (CPIAUCSL); unemployment (UNRATE); sector/breadth proxy.
- Timestamped company-specific and broad-market financial news headlines/article summaries.
- One exchange trading calendar; preserve raw data, record cleaning and produce a data-quality report.
- Reproducible full dataset rebuild from source endpoints.
- Never backfill prices. Align low-frequency macro observations by actual release availability, not merely reference month.

## Feature engineering and EDA (Sections 5–6)
- Returns, moving averages, momentum, RSI, MACD, ATR, volatility, volume and market-context features.
- Sequence-window construction for deep models.
- EDA including distributions, correlations, volatility regimes and stationarity testing (ADF).
- Finance calculations independently verified: returns, covariance, beta, Sharpe and drawdown.

## Models and evaluation (Sections 8–10, 14)
- Classical regressors: Linear/Ridge, Random Forest, XGBoost, SVR.
- Deep sequence architectures: LSTM, GRU, BiLSTM, Transformer.
- Same target, features, chronological split and evaluation period for fair comparison.
- Chronological 70/15/15 is the PRD reference; the project has separately agreed a target-date split for the first one-session experiment (training outcomes through 2023-12-31, validation thereafter until the final six-calendar-month test).
- Train-only preprocessing; early stopping; fixed seeds; no shuffled time split.
- Metrics: RMSE, MAE, MAPE, R² and directional accuracy.
- Naive random-walk baseline must be beaten on MAE and directional accuracy on a genuine held-out test window.

## Sentiment (Section 10)
- Timestamped news by ticker and broad market.
- FinBERT plus VADER comparison.
- Daily sentiment, 3-day momentum and news-volume spike features.
- After-close news maps to the next eligible trading session.
- Report with-vs-without sentiment change in MAE and directional accuracy, whether positive or negative.

## Portfolio and recommendations (Sections 11–12)
- Mean-variance optimisation; efficient frontier; minimum-variance and maximum-Sharpe portfolios.
- Ledoit-Wolf covariance shrinkage and Monte Carlo cross-check.
- Long-only constraints; per-asset concentration cap (example <=30%).
- Backtest against equal-weight and benchmark buy-and-hold on identical out-of-sample dates.
- Report Sharpe, Sortino, volatility, beta, max drawdown, turnover and costs.
- Transparent BUY/HOLD/SELL and rebalancing rules, with educational-not-financial-advice disclaimer.

## Dashboard and deliverables (Sections 13–15)
- Seven dashboard panels: overview; price/prediction; model comparison; portfolio analytics; risk; sentiment; recommendations.
- Streamlit + Plotly; app reads cached outputs and does not retrain on page load.
- Reproducible repository and one-command dataset rebuild / training.
- 10–15 page report with methodology, results and limitations.

## Current implementation gap
The existing market panel is a baseline start only. It does not yet include the complete macro, news/sentiment, point-in-time universe, full EDA, finance-math verification, portfolio, recommendation, dashboard or report deliverables. The new GPU preparation script rebuilds the price/volume-only first experiment; it must not be described as PRD-complete.

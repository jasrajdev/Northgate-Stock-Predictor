# Northgate Stock Predictor: Research Report

**Version:** 15 November 2026. **Scope:** India-focused equity research and decision support.
This report presents the project's methodology, measured results and the practical challenges encountered. Nothing in this report is financial advice.

---

## 1. Executive summary

Northgate is a decision-support research system for ten large Indian equities and the NIFTY 50 index. It forecasts next-session returns with eight model families, converts history into portfolio allocations with mean-variance optimisation, and turns forecasts, risk and sentiment into transparent BUY / HOLD / SELL decisions inside a Streamlit dashboard.

The central empirical result is negative and is reported as such: **on validation data (January 2024 to May 2026), no trained model beat a naive "tomorrow's price equals today's" forecast on mean absolute error.** The closest, a GRU, was 0.70% worse; the best classical model, Ridge regression, 1.73% worse. Directional accuracy for every model lay between 48.8% and 50.3%, against 49.4% for an always-up rule. Because no model has a validated edge, the recommendation engine assigns the forecast zero weight by default and currently recommends **no action** for every stock. The dashboard shows forecasts, but labels them as unvalidated.

The portfolio layer works on historical data: on the same validation window a quarterly-rebalanced, Ledoit-Wolf maximum-Sharpe portfolio returned 20.7% (Sharpe 0.19 at a 6.5% risk-free assumption) against 8.0% for equal weight and 11.1% for the NIFTY 50 price index, after 10 bps per-side costs. This is one period in one market and is not evidence of future outperformance. The held-out test window (11 May to 9 November 2026) is kept separate from model selection and the results reported here; no performance claim is made from that period.

In the application, the four classical models produce forecasts. A key integration challenge was that the four Kaggle deep-model checkpoints expect 32 inputs while the current feature pipeline supplies 25; strict checks prevent incompatible checkpoints from being used. Historical news coverage and API rate limits also constrained the sentiment component, so no sentiment-based performance claims are presented. The exploratory analysis and finance-mathematics verification are delivered as executed notebooks.

## 2. Problem statement and objectives

The PRD asks whether machine-learning forecasts, market context and news sentiment, combined with portfolio optimisation, can support better decisions than simple baselines (PRD §1–2). Its acceptance bar is explicit: the best forecasting model must beat a random-walk predictor on MAE and directional accuracy on a genuine held-out window, and the optimised portfolio must achieve a higher Sharpe ratio than equal weight over the same window (PRD §14.1). The project is research and decision support, not automated trading.

## 3. Data

### 3.1 Universe and market data
Ten NSE equities (BHARTIARTL, HDFCBANK, HINDUNILVR, ICICIBANK, INFY, ITC, LT, RELIANCE, SUNPHARMA, TCS) and the NIFTY 50 price index, daily from 1 January 2016 to 9 November 2026 (10.9 years; 29,484 rows), downloaded from Yahoo Finance with `yfinance` (`auto_adjust=False`, actions included). The universe is a fixed, current large-cap case study, so results are conditional on companies known in 2026 to be large and liquid (survivorship bias; §10).

### 3.2 Data quality findings
A full audit (`reports/claude_dataset_audit_2026-11-14/`) verified the panel, features, labels and splits by exact recomputation, and found:
* **Price basis.** Yahoo's historical prices are back-adjusted: on all 110 symbol-dates checked against official NSE bhavcopy files, Yahoo close equals the official close times the factors of every later split, bonus, rights issue and (for ITC and RELIANCE) demerger, with zero residual. `Adj Close` additionally adjusts for every later dividend. Returns are therefore reliable; historical price *levels* are not what was quoted on the day.
* **Two distorted labels.** Yahoo only partly adjusts the ITC Hotels demerger (6 Jan 2025) and does not adjust the Kwality Wall's demerger of Hindustan Unilever (5 Dec 2025), so two validation labels overstate losses by roughly 1.5–2 percentage points.
* **Bad rows.** 19 equity rows repeat the previous close with zero volume: 10 on 15 Jan 2026 (the exchange was closed) and 9 on 18 Mar 2025 (a normal session). They are flagged in the dashboard and retained without alteration to preserve the source data.
* **Calendar.** Several special sessions (budget-day and Muhurat sessions) are missing for equities, and the index lacks a few dates the equities have.

### 3.3 Market context and macro (implemented, not modelled)
India VIX and seven NIFTY sector indices (Yahoo) and seven FRED series (US 10-year and 3-month yields, US CPI and unemployment, India 10-year and 3-month rates, India central-bank rate) are downloaded and shown in the dashboard. FRED graph downloads return latest-revised values, not point-in-time vintages, so these series are displayed as context but **not used as model inputs**. A point-in-time CPI pipeline for India (MoSPI release events with actual publication times, 18 releases, July 2024 to December 2025) exists and passes its tests, but covers no training rows.

### 3.4 News and sentiment
The PRD requires timestamped financial news with FinBERT and VADER scoring (§10). Implemented: a GDELT DOC API fetcher (titles, URLs and first-seen times only), VADER and FinBERT scorers, after-close mapping to the next NSE session, daily aggregation with three-session momentum and a volume-spike flag. **Challenge encountered:** the free GDELT API provides only a recent rolling window and rate-limited requests during development. Historical coverage was therefore insufficient for a reliable long-range sentiment comparison, and no sentiment performance claim is made.

## 4. Feature engineering

Two feature sets exist (documented in `reports/.../FEATURE_LABEL_DICTIONARY.csv`). Models use **feature set v1** (`src/northgate/features.py`): 25 inputs per stock and session, all computed from the current and earlier sessions only.

| Family | Features |
|---|---|
| Returns | 1, 2, 5, 10 and 20-session simple returns |
| Trend | price relative to 5/10/20/50/100/200-session averages and 12/26-session EMAs; MACD and MACD histogram scaled by price |
| Volatility | 5/10/20/60-session standard deviation of log returns; ATR(14) on the adjusted basis |
| Momentum | RSI(14), Wilder smoothing |
| Volume | volume relative to its 20-session mean; one-session volume change; 20-session on-balance-volume change |
| Level | adjusted close (included to match the Kaggle experiment; see §10) |

A truncation test confirms no feature value at date *t* changes when later data is removed. Target: next-session log return of the adjusted close. Price forecasts are derived as price × exp(forecast).

### 4.1 Exploratory analysis (training period only)
`notebooks/01_eda.ipynb` analyses 2016–2023 only, so it cannot leak later information into modelling choices.

| Finding | Evidence | Decision |
|---|---|---|
| Prices are non-stationary, returns stationary | ADF: unit root not rejected for log prices in 11 of 11 series (p 0.36–0.95); rejected for log returns in 11 of 11 | Forecast returns; benchmark against the random walk |
| Returns are fat-tailed | Excess kurtosis 3.9–22.6; Jarque-Bera rejects normality for every series | Empirical VaR and drawdown; Huber loss for deep models |
| Correlations are moderate and sector-clustered | Mean pairwise 0.28 (0.18–0.58; Infosys–TCS highest) | Ledoit-Wolf covariance, 30% cap |
| Volatility clusters | Lag-1 autocorrelation of returns −0.014, of absolute returns +0.18; NIFTY realised volatility vs India VIX 0.86 | Rolling-volatility features; recent-window risk |
| No seasonality consistent across years | No month consistently positive; one weekday significant in isolation (weak evidence) | No calendar features |

The near-zero autocorrelation of returns anticipated the main forecasting result: past returns alone contain little information about the next session.

### 4.2 Financial mathematics verification
`notebooks/02_finance_math_verification.ipynb` checks every hand-written measure in `src/northgate/finance.py` (returns, annualisation, covariance, correlation, beta, Sharpe, Sortino, maximum drawdown, historical VaR, Calmar, portfolio variance) against independent library calculations on real training-period data; the largest difference is 8.9e-16. A manual batch gradient-descent linear regression (`src/northgate/models/gradient_descent.py`) converges to the closed-form OLS and scikit-learn coefficients on real RELIANCE features (largest difference 1.9e-18). Its training R² is 0.004, again showing little linear predictability.

## 5. Methodology

### 5.1 Chronological partitions
Rows are assigned by the date the outcome becomes known: training targets up to 31 Dec 2023; validation 1 Jan 2024 to 8 May 2026; held-out test 11 May to 9 Nov 2026. Learned preprocessing (imputation, scaling) is fitted on training rows only. Labels after the validation end are never created by the deployment code.

### 5.2 Models
* **Classical, per stock:** Ridge (α = 10), Random Forest (120 trees, min leaf 3), RBF-SVR (C = 1, ε = 0.01), XGBoost (250 trees, depth 4, learning rate 0.04), each inside a median-imputer/standard-scaler pipeline.
* **Deep, pooled across stocks with a ticker one-hot:** LSTM, GRU, bidirectional LSTM and a one-layer Transformer encoder; 30-session input windows; hidden size 24; Huber loss; AdamW; early stopping.
* **Baselines:** naive last adjusted close (zero return) and an always-up direction rule.

### 5.3 Experiment 01 (Kaggle, Tesla T4)
Five expanding validation folds (2024-H1, 2024-H2, 2025-H1, 2025-H2, 2026 to May). Deep models chose their epoch count on the last 15% of each fold's training dates, were refitted on the full fold, and scored once. Run time 83 minutes; 500 result rows. Fixed hyper-parameters and one seed (no tuning; §10).

### 5.4 Deployment models
For the dashboard, the four classical models were re-fitted on this machine's data, on the training partition only, and persisted (`scripts/persist_classical_models.py`). The deep checkpoints from Kaggle are read by a strict loader that rebuilds each architecture from its stored hyper-parameters and applies its own training statistics in its own feature order (`src/northgate/models/deep.py`).

The four Kaggle checkpoints (LSTM, GRU, BiLSTM, Transformer) were installed and **all four are incompatible with the current feature pipeline**. They were trained on 32 inputs: the 25 used here plus seven raw columns (open, high, low, close, volume, dividends, stock splits) that the pipeline deliberately excludes because raw price and volume levels are restated by later corporate actions. The loader refuses them rather than feeding them inputs they were not trained on, so **no deep-model inference is available**. Their validation results in Table 1 come from the Kaggle experiment itself. Using deep models in the application requires retraining them on the 25-input pipeline.

## 6. Results: forecasting (validation only)

**Table 1. Experiment 01, mean over 50 stock-fold results (validation).**

| Model | MAE (₹) | vs naive | RMSE (₹) | MAPE % | Directional accuracy |
|---|---|---|---|---|---|
| Naive (no change) | 18.325 | – | 25.359 | 0.998 | 0.5%* |
| Always-up rule | 18.325 | – | 25.359 | 0.998 | 49.4% |
| GRU | 18.454 | +0.70% | 25.472 | 1.005 | 50.1% |
| BiLSTM | 18.485 | +0.87% | 25.450 | 1.005 | 50.2% |
| Transformer | 18.531 | +1.13% | 25.587 | 1.012 | 50.2% |
| Ridge | 18.643 | +1.73% | 25.716 | 1.015 | 50.3% |
| LSTM | 19.020 | +3.79% | 25.955 | 1.040 | 49.7% |
| Random Forest | 19.992 | +9.10% | 26.938 | 1.078 | 48.8% |
| XGBoost | 20.251 | +10.51% | 27.261 | 1.098 | 49.7% |
| SVR (RBF) | 26.769 | +46.08% | 34.762 | 1.441 | 49.5% |

\* A zero forecast counts as correct only on days with exactly zero return; it is not a measure of directional skill.

Only two of 40 model-fold results fell below the naive error (GRU in 2025-H2 by 0.10%; Transformer in 2024-H2 by 0.000002 rupees, effectively a tie). The local re-fit of the classical models on a single validation split reproduces the Kaggle single-split numbers closely (Ridge 18.49 vs naive 18.01 here; 18.48 vs 18.00 on Kaggle).

**Interpretation.** Next-session prices of large, liquid stocks are dominated by the previous close, so price-level R² is around 0.90 for every model, including the naive one, and carries no evidence of skill. Errors of 0.7–1.7% above naive, without confidence intervals, are consistent with models that learn little beyond noise from price and volume history alone. Tree ensembles and SVR overfit more than the linear and recurrent models. This agrees with the PRD's own caution that deep learning is not automatically superior on modest daily datasets (§9.5).

**Acceptance (PRD §14.1, forecasting):** *not met.* The best model does not beat the random walk on MAE on validation data, so it was not taken to the test window.

## 7. Results: portfolio (validation window)

Weights are re-estimated every 63 sessions from the previous 504 sessions only (historical mean returns, Ledoit-Wolf covariance), long-only with a 30% cap, and charged 10 bps per side on turnover. An efficient frontier and 20,000 random portfolios cross-check the optimiser.

**Table 2. Validation backtest, 1 Jan 2024 to 8 May 2026.**

| Strategy | Total return | CAGR | Volatility | Sharpe | Sortino | Max drawdown | Calmar | Beta |
|---|---|---|---|---|---|---|---|---|
| Max Sharpe (optimised) | 20.7% | 8.5% | 14.1% | 0.19 | 0.26 | −15.3% | 0.56 | 0.80 |
| Minimum variance | 7.9% | 3.4% | 11.9% | −0.21 | −0.29 | −22.5% | 0.15 | 0.72 |
| Equal weight | 8.0% | 3.4% | 12.5% | −0.19 | −0.27 | −18.6% | 0.18 | 0.84 |
| NIFTY 50 price index | 11.1% | 4.7% | 13.9% | −0.07 | −0.09 | −15.8% | 0.30 | 1.00 |

Sharpe uses a 6.5% risk-free assumption. The benchmark excludes dividends while the portfolios include them, which favours the portfolios by roughly the index dividend yield; the Total Returns Index has not been acquired. The maximum-Sharpe result rests on historical means, which are noisy estimators; one favourable period does not establish a durable advantage.

**Validation result:** the optimised portfolio's Sharpe was 0.19 versus −0.19 for equal weight in this validation window. These figures are validation-period results, not held-out performance.

## 8. Recommendation system

Each stock receives `composite = 0.5 × forecast signal + 0.25 × sentiment − 0.25 × max(risk, 0)`, where the forecast signal is the forecast return divided by recent daily volatility (zero if smaller than round-trip cost), sentiment is recent headline polarity, and risk is the stock's volatility relative to the universe. BUY needs a composite of at least 0.5, a positive forecast or sentiment contribution, and room under the 30% cap; SELL needs at most −0.5, a negative contribution and an existing holding; REDUCE applies only above the cap plus a 5% band. Risk can lower conviction but cannot trigger a sale, and a stock is never sold because another has a higher forecast (DECISIONS.md, 12 Nov 2026). If the selected model has no validated edge, the forecast weight is zero. With the current evidence every stock is HOLD and the portfolio-level decision is "no action". A separate rebalancing plan compares current weights with a minimum-variance target (which needs no return forecast) and proposes trades only where drift exceeds the band. All thresholds are configuration (`config/recommendation.json`) and are documented research assumptions, not personalised investment instructions.

## 9. System design

```
data/raw (Yahoo, NSE files) ─► data/processed (panel, features) ─► src/northgate/features.py (v1)
        │                                                              │
        ├─► scripts/persist_classical_models.py ─► models/classical   ├─► models/deep.py ◄─ artifacts/kaggle (checkpoints)
        │                                                              ▼
        └─► finance.py · recommend.py · sentiment.py ─► backend/api.py ─► dashboard/app.py (7 panels)
```

The dashboard (Overview, Price & Prediction, Recommendations, Portfolio Analytics, Risk Dashboard, Sentiment, Model Comparison) reads saved data and persisted models through one backend facade; it never trains or downloads. Model selection, inference availability and every unavailable input are displayed rather than hidden: the Model Comparison panel shows four classical models ready and the four deep checkpoints marked incompatible, and the Sentiment panel shows that no headline data is stored, with the status of each pipeline step. 20 automated tests cover the finance mathematics against hand calculations, backward-looking features, label masking, decision rules (including "no forced trade"), news-to-session timing, a deep-checkpoint round trip for all four architectures, gradient descent against closed-form OLS, persisted classical inference, a check that no source file reads the test split, and a smoke test that renders every dashboard panel.

## 10. Challenges and interpretation

1. **No forecasting edge.** The core forecasting hypothesis is not supported on validation data.
2. **No tuning, one seed, no intervals.** Hyper-parameters were fixed; differences between models are not statistically tested.
3. **Price-level input.** The adjusted close level is a model input; it is restated by later dividends and should be removed in the next experiment.
4. **Vendor data defects.** Back-adjusted prices, two demerger artefacts and 19 stale rows remain in the data used.
5. **Survivorship.** The universe is ten stocks chosen in 2026.
6. **Macro not point-in-time.** Context series are displayed, not modelled.
7. **Historical news coverage.** Available free sources did not provide the long-range, timestamped Indian company news needed for a robust historical comparison.
8. **Benchmark.** Price index, not Total Returns Index.
9. **Portfolio evaluation window.** The portfolio comparison is based on one validation period; the held-out window is kept separate.
10. **Assumed parameters.** Risk-free rate, costs and decision thresholds are documented assumptions.
11. **Deep models not deployable.** The installed Kaggle checkpoints are incompatible with the current feature pipeline, so only the four classical models produce forecasts in the application.

## 11. Reproducibility

See README "Quick start". The notebooks are rebuilt and executed by `scripts/build_notebooks.py`. Exact package versions: `requirements-lock.txt`. Raw data, processed data, model files and Kaggle artefacts are local and git-ignored because of data-provider terms; every derived artefact is rebuilt by a script in `scripts/`. Random seeds are fixed at 42.

## 12. Conclusion

Northgate delivers a working, honest decision-support pipeline: verified data, eight benchmarked model families, a leakage-guarded evaluation, portfolio optimisation with costs, transparent recommendations and an investor-facing dashboard. Its main finding is that daily price and volume history alone did not let any of the eight models beat a no-change forecast for these ten stocks, so the system currently recommends holding. The next research steps are a corrected dataset, scale-free features, tuned models with uncertainty estimates, and context and sentiment inputs with genuine point-in-time timestamps, followed by a single, frozen evaluation on the held-out window.

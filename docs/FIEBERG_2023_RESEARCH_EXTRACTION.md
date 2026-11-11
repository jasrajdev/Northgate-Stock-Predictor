# Research Extraction — Fieberg et al. (2023)

Source: Christian Fieberg, Daniel Metko, Thorsten Poddig, Thomas Loy, “Machine learning techniques for cross-sectional equity returns’ prediction,” OR Spectrum 45 (2023), 289–323. DOI: https://doi.org/10.1007/s00291-022-00693-w.

## Source boundary and accessibility

This extraction is based only on the uploaded full paper PDF (34 substantive PDF pages; journal pages 289–323). No separate supplementary-material file was present among the supplied project files. Consequently, items not established in the article are labelled **NOT STATED IN THIS SOURCE** or **NOT EXPLICITLY ESTABLISHED**. References below use the article's printed page numbers, sections, figures and tables.

## 1. Dataset and universe construction

- **Market:** stocks from countries in the MSCI Developed Markets Europe Index / MSCI Developed Europe universe (Section 4, pp. 304–305).
- **Countries:** the prose says 16 European economies; footnote 13 enumerates Austria, Belgium, Denmark, Finland, France, Germany, Ireland, Italy, Netherlands, Norway, Portugal, Spain, Sweden, Switzerland and the United Kingdom — 15 named countries. The paper's 16-versus-15 count is an internal inconsistency; the source does not reconcile it (p. 305).
- **Period/frequency:** monthly data, January 1990–December 2019 (Section 4, p. 305).
- **Universe size:** “approximately 12,000” individual stocks. Exact distinct-company count and the per-month company-count distribution are **NOT STATED IN THIS SOURCE** (Abstract, pp. 289–290; Section 4, p. 305).
- **Average usable cross-section:** 1,755 firm-month observations per month on average, after requiring nonmissing returns (Table 1 note, p. 305; text p. 306). This is an average, not the total unique-company count.
- **Providers:** Datastream and Worldscope (Section 4, p. 305).
- **Security identification:** Datastream constituent lists — research lists, Worldscope lists and dead lists — are combined for each country; duplicates are removed to leave one list per country. Generic and country-specific screens remove non-common-equity securities. Dynamic screens are then applied to remaining stocks to account for data errors (p. 305).
- **Dead/delisted securities:** the paper explicitly says dead lists are among the Datastream lists used to identify stocks. This supports the statement that dead-list records were part of universe construction. It does **NOT EXPLICITLY ESTABLISH** that every delisted, failed, inactive or otherwise dead security is captured completely throughout the full sample, nor does it quantify dead-list coverage.
- **Inclusion/exclusion screens:** common-equity screening and dynamic data-error screens are described, but the exact generic, country-specific and dynamic screen rules are **NOT STATED IN THIS SOURCE**. Exact exchange-by-exchange inclusion rules are **NOT STATED IN THIS SOURCE**.
- **Survivorship bias:** the design's use of research lists, Worldscope lists and dead lists is intended to construct a broad historical sample; the paper frames its work as addressing U.S. bias and data limitations. It does not give a formal survivorship-bias audit or prove complete point-in-time historical membership. Therefore, calling the dataset definitively survivorship-bias-free is **NOT EXPLICITLY ESTABLISHED**.
- **Coverage limitations:** the paper does not provide a complete per-country start/end coverage audit in the article.

## 2. Learning structure

- The task is **cross-sectional stock-return prediction**, not a single-index time-series forecast (Sections 1–2, pp. 290–294).
- The observation is a **firm-month**: stock i at month t, represented by its firm-characteristic vector x(i,t), with the next month's return r(i,t+1) as the outcome (Section 3, p. 295, Eqs. 3–4).
- The model estimates one common prediction function g(.) over the panel. Pooled OLS is explicitly written as minimising error across stocks i and months t (Eq. 6, p. 295). The machine-learning models are also supplied with the same panel data.
- The six stock characteristics differ across firms and dates; the model uses those cross-sectional characteristics to explain differences in next-month returns.
- It uses information across both stocks and time: cross-sectional observations at each month are pooled over a rolling historical estimation period.
- It is therefore a pooled panel-learning design. The authors do not train a separate model for each company.
- A controlled comparison of pooled models versus separate per-company models is **NOT STATED IN THIS SOURCE**. The paper does not establish that pooled learning is superior to individual-stock training for a small universe.
- Section 2 distinguishes time-series prediction of one aggregate index from cross-sectional prediction of many stocks at a point in time (pp. 293–294, Eqs. 1–2).

## 3. Prediction target

- **Target:** next-month individual-stock return, r(i,t+1), not the future price level (Section 3, p. 295, Eqs. 3–4).
- It is a continuous regression target. The paper predicts expected returns and then sorts stocks by predicted return; it is not a BUY/HOLD/SELL classification model.
- The dependent variable is called stock return / total return. Datastream total return index (RI) is the named source variable (Section 4, pp. 305–306).
- Whether the return is expressed as a simple return or logarithmic return is **NOT STATED IN THIS SOURCE** in the variable definition available in the article.
- The paper does not define its dependent variable as excess return in the model equations; the text and tables generally call it stock return. Market excess return is used separately to define bull/bear regimes (p. 315).
- Exact dividend/corporate-action mechanics behind the Datastream total return index are **NOT STATED IN THIS SOURCE**.
- **Horizon/frequency:** one month ahead; monthly observations (Sections 3–4, pp. 295, 305–306).
- **Alignment:** characteristics at month t predict return at t+1 (Eqs. 3–6, p. 295). Market capitalisation screens use prior-month market values (p. 307). Beta uses daily returns from the previous 12 months (p. 306). Accounting data are assumed publicly available six months after fiscal year-end (p. 306).
- Exact within-month timestamp / market-close convention for every characteristic is **NOT STATED IN THIS SOURCE**.

## 4. Six-variable predictor inventory

The authors deliberately use a sparse set of six established firm characteristics to compare models on a common, relatively low-dimensional feature set and reduce the risk that ML gains merely reflect a huge predictor set (pp. 290–291).

| Variable (paper term) | Definition/source stated in paper | Frequency/timing stated | Transformation/missingness |
|---|---|---|---|
| Beta (beta) | Exposure to the market factor derived from CAPM. Estimated for each month using daily stock returns over the previous 12 months (p. 306). | Monthly estimate; trailing prior 12 months. | Cross-sectional rank normalisation; missing characteristic replaced by cross-sectional median when return is available. |
| Market capitalisation (size) | Market equity (Datastream MV); table labels size as log market capitalisation, in millions (Table 1 note, p. 305; p. 306). | Market equity at month-end is used in cross-sectional size screens; exact update mechanics beyond monthly panel are **NOT STATED IN THIS SOURCE**. | Cross-sectional rank normalisation; median imputation if return is present. |
| Book-to-market equity (be2me) | Book equity / market equity; book equity is Worldscope WC03501 and market equity is Datastream MV (pp. 305–306). | Accounting data assumed public six months after fiscal year-end to avoid look-ahead (p. 306). Exact refresh cadence is **NOT STATED IN THIS SOURCE**. | Cross-sectional rank normalisation; median imputation if return is present. |
| Momentum (mom) | Total return over the prior 12 months, excluding the most recent month (p. 306). | Monthly; trailing 12-month return with last month excluded. | Cross-sectional rank normalisation; median imputation if return is present. |
| Investment (inv) | Growth in total assets; Worldscope WC08621 (pp. 305–306). | Accounting data assumed public six months after fiscal year-end (p. 306); exact update cadence is **NOT STATED IN THIS SOURCE**. | Cross-sectional rank normalisation; median imputation if return is present. |
| Operating profitability (op) | Operating income scaled by book value of equity; Worldscope WC01250 and WC03501 (pp. 305–306). | Accounting data assumed public six months after fiscal year-end (p. 306); exact update cadence is **NOT STATED IN THIS SOURCE**. | Cross-sectional rank normalisation; median imputation if return is present. |

Additional points:
- Selection rationale: the six variables are drawn from established asset-pricing literature and are the building blocks of Fama–French three-factor, Carhart four-factor and Fama–French five-factor models (pp. 290–291, 306).
- The authors state the variables are selected so that they are available over the entire sample and there are no large deviations in missing data between predictors in the cross-section (pp. 291–292).
- All models receive the same six predictors (the same data) (p. 302). The paper does not describe adding interactions or external macro features to the main six-variable design; additional features are **NOT STATED IN THIS SOURCE**.
- The paper's rationale is to avoid irrelevant predictors and overfitting from very large feature sets. It does not claim these are the six best predictors for every market (pp. 290–292).

## 5. Missing data, outliers and preprocessing

- **Missing characteristics:** if a firm's return is available but a characteristic is missing, the characteristic is replaced with the cross-sectional median for that month (p. 307).
- **Missing returns:** the analysis includes only firm-month observations with nonmissing returns; the paper does not impute missing dependent-variable returns (p. 306).
- **Entire missing cross-sections:** unlike much of the literature discussed, the authors say they have observations on each characteristic in every month and do not fill entire cross-sections with zeros (pp. 291–292, 307).
- **Rank normalisation:** different scales and extreme observations are handled by cross-sectionally rank-normalising firm characteristics (p. 307). Earlier, the paper explains that rank-transformed characteristics are mapped to [-1, 1], making the cross-sectional mean/median zero (p. 291). The exact rank formula / tie treatment is **NOT STATED IN THIS SOURCE**.
- **Outliers:** rank normalisation is the stated method to handle extreme observations. Separate winsorisation, trimming or z-score procedures are **NOT STATED IN THIS SOURCE**.
- **Date-specific treatment:** “cross-sectionally” rank normalising and imputing implies operations over the cross-section for a month; the article does not spell out a complete implementation algorithm for each preprocessing step.
- **Point-in-time availability:** explicit timing safeguards include a six-month accounting-data lag and beta estimated from the prior 12 months of daily returns (p. 306). The article does not explicitly prove that every input and each preprocessing statistic is computed strictly using only data available at every historical prediction timestamp. Therefore, a complete preprocessing leakage audit is **NOT EXPLICITLY ESTABLISHED**.
- The authors' critique of zero-filling is that it may matter materially when characteristics are unavailable for long historical periods; they choose variables with broad availability and do not zero-fill missing cross-sections (pp. 291–292).

## 6. Training, validation and testing

- Each model uses a **ten-year rolling window of monthly panel data** and forecasts returns for the subsequent year (p. 302).
- Each ten-year in-sample window is divided chronologically into **seven years of training** and **three years of validation**; grid search selects hyperparameters on validation data (pp. 302–303; Fig. 4, p. 303).
- After selecting hyperparameters, the model is re-estimated on the complete ten-year training-plus-validation window, then used to forecast the following year. The actual forecast period does not enter estimation (p. 303).
- The figure and text describe a rolling estimation scheme. The implied refit cadence is once per forecast year, but the exact implementation details for how the first/last partial windows are handled are **NOT STATED IN THIS SOURCE**.
- The paper says retaining temporal ordering mimics a realistic prediction scenario (footnote 11, p. 302).
- **Timeline (conceptual):**

| Stage | Historical data used | Purpose |
|---|---|---|
| Training | First 7 years of the 10-year estimation window | Fit candidate model/hyperparameters |
| Validation | Final 3 years of that same 10-year window | Grid-search selection |
| Refit | Full 10-year window (7 + 3 years) | Re-estimate with selected settings |
| Forecast/test | Subsequent year | Out-of-sample prediction/evaluation |
| Roll forward | Move the estimation window forward for the next forecast year | Repeat |

- Test-date reporting is inconsistent: p. 304 describes the testing period as January 2001–December 2019, while notes to Tables 2 and 4 describe predictions/testing from January 2000–December 2019 (pp. 305, 307–308, 312). The article does not reconcile this discrepancy.
- No shuffled k-fold cross-validation is described. The explicit method is chronological train/validation with a rolling out-of-sample forecast procedure.
- All models use the same data / ten-year rolling period (p. 302).
- The source explicitly describes past-only forecasting and a six-month accounting-data lag and prior-12-month beta (pp. 302–303, 306). It does not discuss purging overlapping labels; overlapping-label treatment is **NOT STATED IN THIS SOURCE**.
- Figure 4 (p. 303) illustrates the rolling estimation scheme. The printed page shows the timeline; the table above restates only what the adjacent text explicitly specifies.

## 7. Model inventory and implementation

The models actually compared are OLS, Lasso, Ridge, Elastic Net, SVR, Random Forest (RF), Gradient Boosted Regression Trees (GBRT), and feed-forward Neural Networks (NN) (Sections 3.1–3.4, pp. 295–302; Table 2, p. 307).

| Model | Implementation details stated in source |
|---|---|
| OLS | Pooled linear regression over firm-month observations; minimise average squared forecast error (Eq. 6, p. 295). |
| Lasso | Elastic-net special case with rho=0; sparse penalty can set coefficients exactly to zero (pp. 295–296). |
| Ridge | Elastic-net special case with rho=1; shrinks coefficients toward zero without forcing exact zeros (p. 296). |
| Elastic Net | Mix of Lasso and Ridge; rho=0.5 in the empirical application (p. 296; Table 11, p. 320). |
| SVR | Epsilon-insensitive regression with slack variables and l2 regularisation; RBF kernel; grid search for epsilon, C/lambda and gamma (pp. 296–298; Eqs. 9–13). |
| RF | Bootstrap aggregation of B trees; random subset of p predictors at each split; average tree predictions (p. 300, Eq. 16). |
| GBRT | Sequential additive trees fitted to prior residuals; learning-rate shrinkage nu controls each tree's contribution (p. 300, Eq. 17). |
| NN | Feed-forward network with one hidden layer, tanh hidden activation, linear output; hidden-neuron count set to twice input count; Adam optimiser; l2 weight decay; early stopping after validation error fails to improve for ten consecutive iterations; ensemble of ten networks averaged (pp. 301–302). |

Grid-search ranges / settings from Table 11 (p. 320):
- Lasso: lambda in [10^-4, 10^-1].
- Ridge: lambda in [10^-4, 10^-1].
- Elastic Net: rho/alpha = 0.5; lambda in [10^-4, 10^-1].
- SVR: gamma in [10^-1, 10^3]; C in [10^-1, 10^3]; epsilon in [10^-3, 10^-1]. The article's footnote relates C to inverse regularisation lambda.
- RF: B = 300; tree depth J in [1, 10]; candidate predictor count p in {2, 5}.
- GBRT: B in [1, 2500]; J in {1, 5}; learning rate nu in [10^-2, 10^-1].
- NN: L = 2 (the article's layer notation includes output layer, while prose specifies a single hidden layer); K = 12; activation tanh; learning rate in [10^-3, 10^-2]; lambda in [10^-5, 10^-3].
- Exact grid point spacing / number of candidate values inside continuous ranges is **NOT STATED IN THIS SOURCE**.
- Neural-network optimiser is Adam; exact batch size and other implementation details are **NOT STATED IN THIS SOURCE**.
- RF/GBRT tree criteria and all software/library versions are **NOT STATED IN THIS SOURCE**.
- SVR uses RBF kernel K(x,z)=exp(-gamma ||x-z||^2) (Eq. 13, p. 298); epsilon-insensitive loss is defined in Eq. 10 (p. 296).
- Forecast combinations are also tested: equal weights (EW), inverse in-sample MSE weights (IMSE), and inverse MSE-rank weights (IRANK), for combinations of all models and nonlinear models only (Eqs. 24–25, pp. 316–317).

## 8. Stock-size and liquidity experiments

- The authors repeatedly remove stocks below successive cross-sectional market-capitalisation quantiles q = 0.0, 0.1, …, 0.9 (pp. 304, 307). “Size > q” therefore means retaining stocks above the relevant cross-sectional size cutoff, not selecting a fixed percentage of a pre-existing small stock list.
- Market capitalisation is market equity / size (Datastream MV); the size variable is described as log market capitalisation in millions (Table 1 note, p. 305; p. 306).
- The cutoffs are cross-sectional and are applied using prior-month market values (p. 307). The exact numeric currency thresholds are not reported; the quantile thresholds move with the monthly cross-section.
- **Largest 10% retained:** q = 0.90 / Size > q90. This is a subset of the full ~12,000-stock European universe, not a small-universe experiment.
- The article does not test a universe of 50–100 stocks or Northgate's 8–15 stocks. It establishes no minimum viable stock count and does not compare pooled versus individual-stock models (NOT STATED IN THIS SOURCE).
- Predictive R2 falls as smaller firms are removed. Table 2 (p. 307), full sample to largest 10%:
  - OLS: 0.43% to -0.32%.
  - Lasso: 0.40% to -0.39%.
  - Ridge: 0.42% to -0.29%.
  - Elastic Net: 0.37% to -0.35%.
  - SVR: 0.14% to -0.58%.
  - RF: 0.58% to -0.45%.
  - GBRT: 0.60% to 0.14%.
  - NN: 0.67% to 0.24%.
- At q=0.90, only GBRT and NN remain positive on the table's predictive R2 metric (Table 2, p. 307).
- Economic performance (Table 5, p. 312), full sample to largest 10%, monthly long-short spread:
  - OLS: 1.74% to 0.53%.
  - Lasso: 1.79% to 0.48%.
  - Ridge: 1.73% to 0.55%.
  - Elastic Net: 1.78% to 0.58%.
  - SVR: 1.77% to 0.73%.
  - RF: 2.38% to 0.46%.
  - GBRT: 2.33% to 0.59%.
  - NN: 1.83% to 0.70%.
- RF's full-universe advantage falls sharply after excluding the smallest stocks; the authors interpret this as RF capturing microcap dynamics. GBRT and NN retain predictive advantage over OLS across size segments; SVR's economic spreads are comparatively strong despite weaker statistical R2 (pp. 307–308, 312–313).
- This is a size/liquidity robustness experiment across a very broad cross-section. It is not evidence that the same models will work on 8–15 large-cap stocks.

## 9. Predictive results and statistical performance

- Main metric: monthly out-of-sample panel R2, reported as a percent, benchmarked against a zero-return forecast (pp. 303–304, 307).
- The paper's R2 sets the benchmark return r-bar to zero, rather than the historical average, because the authors consider the latter to inflate R2 in a stock-return panel (p. 303).
- Full Table 2 results (p. 307):

| Size > q | OLS | Lasso | Ridge | Enet | SVR | RF | GBRT | NN |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.43 | 0.40 | 0.42 | 0.37 | 0.14 | 0.58 | 0.60 | 0.67 |
| 0.10 | 0.36 | 0.33 | 0.34 | 0.28 | 0.15 | 0.36 | 0.44 | 0.63 |
| 0.20 | 0.36 | 0.32 | 0.34 | 0.27 | 0.19 | 0.36 | 0.45 | 0.66 |
| 0.30 | 0.36 | 0.30 | 0.34 | 0.27 | 0.20 | 0.35 | 0.46 | 0.68 |
| 0.40 | 0.35 | 0.29 | 0.33 | 0.26 | 0.20 | 0.34 | 0.47 | 0.70 |
| 0.50 | 0.31 | 0.24 | 0.30 | 0.23 | 0.17 | 0.27 | 0.46 | 0.70 |
| 0.60 | 0.26 | 0.18 | 0.25 | 0.19 | 0.12 | 0.20 | 0.45 | 0.67 |
| 0.70 | 0.17 | 0.08 | 0.17 | 0.11 | -0.01 | 0.09 | 0.43 | 0.63 |
| 0.80 | -0.03 | -0.10 | -0.01 | -0.06 | -0.26 | -0.17 | 0.32 | 0.50 |
| 0.90 | -0.32 | -0.39 | -0.29 | -0.35 | -0.58 | -0.45 | 0.14 | 0.24 |

- Full sample: RF 0.58%, GBRT 0.60%, NN 0.67%, versus OLS 0.43%. The paper describes ML gains of approximately 0.6 percentage points per month for the best model on the full cross-section (Abstract, pp. 289–290; Table 2, p. 307).
- Largest 10%: GBRT 0.14% and NN 0.24%; other models are negative (Table 2, p. 307).
- Pairwise Diebold–Mariano tests compare predictive accuracy (Table 3, p. 308). Full-sample results show RF, GBRT and NN significantly outperforming linear models/SVR at reported low p-values; pairwise differences among RF, GBRT and NN are not statistically distinguishable in the reported comparisons. For the largest 10%, GBRT and NN retain significant advantages over other methods in the reported table.
- The authors note SVR is below OLS on predictive R2 and may be sensitive to low-impact predictors and hyperparameters (p. 308).
- Bull/bear results (Table 7, p. 314): predictability is generally higher in bull markets; bear-market R2 is generally negative and declines with firm size. NN has the highest R2 and outperformance versus OLS in both regimes. Example full sample: bull R2 OLS 1.22%, NN 1.29%; bear OLS -0.40%, NN 0.03%.
- The paper uses Diebold–Mariano tests, t-tests on long-short returns and Patton–Timmermann monotonicity tests (Tables 3–4, pp. 308–310). Exact test assumptions beyond the described procedures are **NOT STATED IN THIS SOURCE**.

## 10. Portfolio and economic evaluation

- At each month-end, the models forecast next-month returns; stocks are sorted into ten equal-weighted decile portfolios using cross-sectional forecast breakpoints. The long-short, zero-net-investment portfolio buys the top decile and shorts the bottom decile (pp. 304, 308–310).
- Table 4 reports average return (Avg), standard deviation (Std), Sharpe ratio (Shp) and average predicted return (Pred). The full-sample high-minus-low (H-L) monthly spread and Sharpe values are:

| Model | H-L average monthly return (%) | H-L Std (%) | H-L Sharpe |
|---|---:|---:|---:|
| OLS | 1.74 | 5.09 | 0.34 |
| Lasso | 1.79 | 5.36 | 0.33 |
| Ridge | 1.73 | 5.21 | 0.33 |
| Elastic Net | 1.78 | 5.60 | 0.32 |
| SVR | 1.77 | 4.96 | 0.36 |
| RF | 2.38 | 4.90 | 0.48 |
| GBRT | 2.33 | 4.16 | 0.56 |
| NN | 1.83 | 4.38 | 0.42 |

  Source: Table 4, pp. 309–310. GBRT has the highest reported H-L Sharpe (0.56); RF has the highest H-L average return (2.38%). The article reports GBRT's Sharpe as 1.94 annualised (p. 312).
- Table 5 reports the H-L return spread across size thresholds; see Section 8 above (p. 312).
- Turnover is measured as average monthly changes in holdings for the spread portfolios (Eq. 23, pp. 313–314). Table 6 (p. 313) reports turnover percentages:

| Size > q | OLS | Lasso | Ridge | Enet | SVR | RF | GBRT | NN |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 125 | 124 | 124 | 125 | 133 | 154 | 144 | 132 |
| 0.10 | 125 | 125 | 126 | 126 | 131 | 152 | 143 | 131 |
| 0.20 | 124 | 126 | 123 | 126 | 131 | 152 | 141 | 133 |
| 0.30 | 125 | 126 | 124 | 125 | 131 | 153 | 140 | 131 |
| 0.40 | 124 | 126 | 124 | 124 | 129 | 154 | 140 | 133 |
| 0.50 | 125 | 128 | 125 | 126 | 129 | 151 | 140 | 133 |
| 0.60 | 127 | 129 | 128 | 129 | 127 | 150 | 141 | 131 |
| 0.70 | 128 | 129 | 128 | 129 | 127 | 147 | 140 | 127 |
| 0.80 | 127 | 129 | 128 | 129 | 127 | 144 | 138 | 127 |
| 0.90 | 126 | 129 | 127 | 130 | 129 | 142 | 140 | 127 |

- Authors say RF/GBRT turnover is generally higher (tree-based methods about 20% higher for RF relative to OLS in their discussion), while penalised linear models, SVR and NN have turnover comparable to OLS (pp. 313–314).
- The authors explicitly say realistic transaction costs are difficult to observe and estimate. Their analysis compares turnover; it does not deduct a fully specified realistic brokerage, spread, market-impact, tax and slippage schedule from portfolio returns (pp. 313–314). Thus fully transaction-cost-adjusted profitability is **NOT EXPLICITLY ESTABLISHED**.
- The zero-investment portfolio is long-short and equally weighted within deciles; it is not a long-only retail portfolio or a mean-variance allocation. The article does not test Northgate's portfolio optimisation or BUY/HOLD/SELL rules.
- Bull/bear strategy results are in Table 8 (pp. 316–317). The market state is defined by whether trailing 12-month cumulative market excess return is positive (bull) or negative (bear) (p. 315). The authors report that model differences are more visible in bear markets; SVR and NN have consistently higher returns than OLS in bear markets, including roughly 40 basis points difference for the largest 10% (pp. 315–317).
- Forecast combinations: equal-weight, inverse-MSE and inverse-MSE-rank weighting are tested for all models and nonlinear-only models. Table 9 reports monthly predictive panel R2; Table 10 reports long-short returns (pp. 317–318). Nonlinear-only combinations have higher predictive R2 than combinations including linear methods; all combinations outperform OLS but do not exceed the best individual NN on predictive accuracy. Economically, combinations can outperform best individual SVR up to Size > 0.7 (pp. 317–319).

## 11. Author-stated limitations and transferability

- The paper's central motivation includes overfitting/irrelevant predictors, missing data and U.S.-market research bias (pp. 290–292).
- The empirical universe is European, not Indian; the results are not an India-market test.
- The data are monthly, not daily.
- The predictor set is six established firm characteristics, not a broad OHLCV technical-feature set or timestamped news/sentiment feature set.
- The universe is broad (approximately 12,000 stocks), not a small portfolio of 8–15 names.
- The authors note small stocks are more difficult and costly to trade and that apparent predictability may be more apparent than real when microcaps are included (pp. 304, 313).
- Future research should examine ML for long-term stock returns more closely (Conclusion, p. 319).
- The article's explicit author-stated future direction does not provide an India-specific transfer method. What will transfer to India is **NOT EXPLICITLY ESTABLISHED**.

## 12. What this paper does NOT establish

| Question | What the source supports |
|---|---|
| Minimum viable stock count | **NOT STATED IN THIS SOURCE.** |
| Performance with 8–15 stocks | **NOT STATED IN THIS SOURCE.** |
| Performance in Indian equities | **NOT STATED IN THIS SOURCE.** |
| Pooled versus individual-stock superiority | **NOT STATED IN THIS SOURCE.** It uses a pooled panel; no head-to-head architecture test. |
| Daily versus monthly forecasting superiority | **NOT STATED IN THIS SOURCE.** The study uses monthly data only. |
| Universal optimal training-window length | **NOT STATED IN THIS SOURCE.** Ten years is this study's design. |
| Universal feature set | **NOT STATED IN THIS SOURCE.** Six features are selected for this study. |
| Fully transaction-cost-adjusted profitability | **NOT EXPLICITLY ESTABLISHED.** Turnover is reported, but no full realistic cost deduction. |
| Sufficiency of six features for Northgate | **NOT STATED IN THIS SOURCE.** |
| Deep sequence model superiority | **NOT STATED IN THIS SOURCE.** Its NN is a feed-forward network, not LSTM/GRU/Transformer. |
| News/sentiment incremental value | **NOT STATED IN THIS SOURCE.** No news features are tested. |
| Portfolio weights / mean-variance optimisation | **NOT STATED IN THIS SOURCE.** |
| BUY/HOLD/SELL recommendation performance | **NOT STATED IN THIS SOURCE.** |
| Complete survivorship-bias-free universe | **NOT EXPLICITLY ESTABLISHED.** Dead lists are used, but completeness is not audited. |

## 13. Source inconsistencies and unresolved details

1. The prose says 16 European economies, but footnote 13 lists 15 countries (p. 305).
2. The testing period is described as January 2001–December 2019 on p. 304, while table notes report January 2000–December 2019 (pp. 307, 312).
3. The exact distinct number of firms and monthly minimum/maximum cross-sectional counts are not provided; “nearly 12,000” and average N=1,755 are the reported figures.
4. Dead lists are named, but the completeness of historical delisted-security coverage is not demonstrated.
5. Detailed constituent-screen rules, exact rank transform, missing-data edge cases, software versions and some implementation settings are not provided.
6. Fully realistic transaction costs are not estimated/deducted.

## 14. Evidence summary for Northgate research

### Directly established by this paper
- A pooled cross-sectional panel of firm-month observations can be used to forecast next-month stock returns from lagged firm characteristics.
- The authors test eight approaches (OLS, Lasso, Ridge, Elastic Net, SVR, RF, GBRT, NN) using the same six predictors and a rolling ten-year monthly estimation window.
- The paper uses seven years for training and three for validation, then refits on the full ten-year window and forecasts the following year.
- Cross-sectional median imputation, cross-sectional rank normalisation, six-month accounting-data lag and trailing-12-month beta are explicitly described.
- In the study's broad European universe, GBRT and NN show the strongest predictive R2 results; results weaken materially as smaller stocks are removed.
- Long-short portfolio spreads and turnover are evaluated separately from statistical forecast accuracy.

### What remains unknown
- Whether any of these results hold in India, for daily data or for 8–15 equities.
- Whether pooled learning is better than per-stock models in a small universe.
- Whether the six features can be constructed with comparable coverage and point-in-time integrity for Indian stocks.
- Whether the paper's apparent economic gains survive a complete realistic cost model.
- Whether a sequence model, sentiment pipeline or mean-variance optimiser adds value to this design.

### What is Europe-specific
- The universe, providers, country coverage, market structure, monthly sample and observed feature/return relationships are European.
- The size/liquidity effects and reported model rankings belong to this sample and methodology; they should not be transplanted to India without separate evidence.

### Questions requiring further research
- How do Indian-market studies construct historical universes, include delisted securities and time-align accounting data?
- Can a pooled model be validated meaningfully with only 8–15 names, or is a broader panel necessary?
- How do daily OHLCV forecasting tasks compare with monthly cross-sectional return ranking?
- What data coverage and point-in-time timing can be achieved for the six firm characteristics in India?
- What transaction-cost assumptions are defensible for Indian equities and the intended holding horizon?

## References within the source
- Dataset and universe: Section 4, pp. 304–306; Table 1, p. 305.
- Cross-sectional versus time-series task: Section 2, pp. 293–294.
- Model equations: Section 3, pp. 295–302.
- Rolling estimation: Section 3.5, pp. 302–304; Fig. 4, p. 303.
- Main predictive results: Table 2, p. 307; Table 3, p. 308.
- Portfolio results: Table 4, pp. 309–310; Table 5, p. 312.
- Turnover: Table 6, p. 313.
- Bull/bear and forecast combinations: Tables 7–10, pp. 314–318.
- Hyperparameter ranges: Table 11, p. 320.

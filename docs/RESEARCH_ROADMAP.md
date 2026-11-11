# Research Synthesis & Progress — Northgate Stock Predictor

Updated: 2026-11-12

## Purpose

This is the **single rolling research document** for Northgate. It preserves the useful, cumulative conclusions from reviewed sources, how the evidence changes our understanding, what remains unresolved, and what source we should examine next.

Do not create a separate teaching/summary document for every paper. Do not store full prompts or lengthy paper-by-paper notes here. Keep source identities and review status for traceability, but continuously refine the synthesis below as new evidence arrives.

## Research discipline

- Use freely accessible full-text sources as the default. Do not recommend a paid paper as a required source.
- Distinguish the source's reported findings from our interpretation and from approved Northgate decisions.
- Record page, section, table, figure or appendix references for important claims.
- If a source does not state something, record **“Not stated in source.”**
- Do not transfer US/European results directly to Indian equities without validation.
- No research finding becomes a project decision until its relevance is discussed and the user explicitly agrees.
- Preserve contradictory evidence rather than silently choosing one study's result.
- Keep the PRD scope intact unless the user approves a change.

## Sources reviewed / queued

| # | Source | Access and review status | Role in the research |
|---|---|---|---|
| 1 | Lalwani & Meshram (2022), [The cross-section of Indian stock returns: evidence using machine learning](https://doi.org/10.1080/00036846.2021.1982132) | **Abstract/metadata only.** The available three-page file was a publisher landing-page printout, not the 15-page article. Full text not found free; do not pay for it. | Retain only limited abstract-level context about an Indian-market study; methodology remains unverified. |
| 2 | Gu, Kelly & Xiu (2020), [Empirical Asset Pricing via Machine Learning](https://doi.org/10.1093/rfs/hhaa009) — [free NBER PDF](https://www.nber.org/system/files/working_papers/w25398/w25398.pdf) | **Full-paper extraction reviewed.** The supplied extraction reports an 80-page NBER Working Paper 25398, dated December 2018 and revised September 2019. Treat that version as distinct from the final 2020 journal version unless checked. | Large US cross-sectional panel; pooled learning; predictor construction and timing; chronological evaluation; model and portfolio comparisons. |
| 3 | Fieberg et al. (2023), [Machine learning techniques for cross-sectional equity returns’ prediction](https://doi.org/10.1007/s00291-022-00693-w) — [free open-access full text](https://link.springer.com/article/10.1007/s00291-022-00693-w) | **Next source to review.** Publisher confirms open access and full text. | Independent European-market comparison; sparse six-feature design; missing data and outlier handling; rolling-window evaluation; size/liquidity sensitivity; SVR and model comparisons. |
| 4 | Chen, Pelger & Zhu (2024), [Deep Learning in Asset Pricing](https://doi.org/10.1287/mnsc.2023.4695) | Pending; use only if freely accessible full text/supplement is available. | Deep-learning asset-pricing evidence and whether it adds anything material to the current dataset/model questions. |
| 5 | [Stock picking with machine learning](https://doi.org/10.1002/for.3021) | Optional; review only if full text is freely accessible and it fills a specific remaining gap. | Possible additional stock-selection design; not required by default. |

## Cumulative research synthesis

The following is the current evidence-informed understanding. It is a **research synthesis, not an approved Northgate specification**.

### 1. Prediction task and learning structure

- The reviewed evidence includes cross-sectional return prediction: predicting differences in future returns across multiple stocks, rather than simply forecasting one index time series.
- A pooled panel model is a credible research design: one common function can be estimated from stock-month observations and then produce a separate prediction for each stock.
- In the Gu–Kelly–Xiu study, stock identity is not itself the learned function; stock-level characteristics and common macro inputs represent differences between stocks and time periods.
- This does **not** establish that pooled models outperform separate models for a small universe. The reviewed study does not run a controlled small-universe comparison.
- Keep cross-sectional stock selection distinct from aggregate-market/index time-series forecasting. They are different prediction problems and may need different datasets and baselines.

### 2. Target and frequency

- The Gu–Kelly–Xiu extraction reports a primary target of next-month individual-stock **excess return**, not stock price, with monthly total-return data and a Treasury-bill risk-free adjustment.
- The Indian paper's accessible abstract also refers to stock returns and rolling one-month-ahead forecasts, but its full target formula is unavailable.
- These provide monthly return-prediction precedents; they do not prove monthly is best for Northgate. The PRD's daily data requirement and intended prediction/holding horizon still need to be reconciled experimentally.
- Keep price prediction, total return, excess return, directional classification and cross-sectional ranking clearly distinct. Do not choose one target yet.

### 3. Predictors and feature design

- Gu–Kelly–Xiu's reported baseline combines 94 stock characteristics, 8 macroeconomic predictors and 74 industry indicators, producing 920 baseline covariates after characteristic–macro interactions.
- That is evidence of one large research design, not a requirement for Northgate to use 920 features.
- The next useful comparison is Fieberg et al., which uses a deliberately sparse set of six established firm characteristics. Comparing these studies can help us understand the trade-off between broad feature sets and sparse, controlled predictor sets.
- Feature availability and timing matter as much as feature names. Accounting characteristics need publication lags; a feature must only enter a prediction after it would actually have been available.
- We still need Indian-market evidence for data availability, definitions, update frequency and point-in-time timing.

### 4. Data quality and universe integrity

- The Indian paper's abstract claims a survivorship-bias-free sample, but the accessible document does not explain how that was implemented.
- Gu–Kelly–Xiu use a broad historical US equity panel with a changing number of stocks, but the supplied extraction does not establish all delisting and historical-membership details.
- Therefore, historical universe membership, delisted firms, bankruptcies, corporate actions, symbol changes and survivorship bias remain critical open questions for Northgate.
- Gu–Kelly–Xiu report monthly cross-sectional median imputation for missing characteristics and cross-sectional rank scaling to [-1, 1]. This is a source-specific method, not an automatic Northgate choice.
- We need to examine whether other studies use different missing-data and outlier approaches, and whether preprocessing is performed with only information available at each historical prediction time.

### 5. Training and evaluation

- Gu–Kelly–Xiu's reported design uses chronological training, validation and test periods; an expanding training sample; a rolling 12-year validation window; and annual model refitting.
- They do not use shuffled cross-validation.
- This provides a concrete example of time-ordered evaluation, but its very long historical windows and annual refitting are not automatically suitable for Northgate's shorter 8–10-year PRD dataset.
- Preserve the principle: validation/tuning must not use the final test period, and every feature/preprocessing step must respect the historical information set.
- The supplied extraction leaves some preprocessing-fit details unresolved; do not label every operation leakage-free without checking it.

### 6. Model comparisons and complexity

- Gu–Kelly–Xiu compare linear, regularised, dimension-reduction, tree-based and feed-forward neural-network models. Their reported best stock-level neural network is a relatively shallow three-hidden-layer? **Correction: the supplied extraction describes NN3 as three hidden layers (32, 16, 8 neurons), and reports it outperforming their deeper NN4/NN5 variants.**
- Their result supports testing nonlinear models against simple baselines; it does not establish that deep learning is always superior or that their architecture transfers to a small Indian sample.
- The next study is valuable because it includes SVR and compares several ML methods using a sparse predictor set, directly overlapping with parts of the Northgate PRD.
- Northgate must still compare the PRD-required model families on the same dates, target and information set, with simple baselines.

### 7. Economic evaluation

- Forecast accuracy and investment performance are separate evaluation layers.
- Gu–Kelly–Xiu aggregate individual-stock forecasts into portfolios and test forecast-sorted long–short strategies. Their reported portfolio results are sensitive to micro-cap inclusion.
- The supplied extraction does not establish a complete realistic transaction-cost model covering brokerage, taxes, slippage and market impact.
- Do not use reported Sharpe ratios or returns as Northgate targets. Northgate needs Indian-market costs, liquidity constraints, turnover and realistic execution assumptions.

## Open questions that remain important

1. What is the right prediction problem for Northgate: cross-sectional ranking of stocks, individual-stock return prediction, index time-series forecasting, or a clearly separated combination?
2. Can pooled learning work with the PRD's 8–15 equities, or should pooled and per-stock approaches be compared?
3. What is the effect of training on 8–10 years of daily data versus a longer monthly/weekly panel?
4. Which target and horizon align with the intended recommendations and portfolio evaluation?
5. Which features are available reliably and point-in-time for Indian equities?
6. How can we obtain historical NSE/BSE universe membership, delisted securities and corporate-action-adjusted returns?
7. What missing-data and outlier procedures are defensible without leakage?
8. How should preprocessing be fitted and recomputed in each chronological training window?
9. What performance survives Indian brokerage, statutory charges, bid–ask spread, slippage, turnover and liquidity limits?
10. Which required model families can be trained and evaluated credibly with the available data and deadline?

## Next research step

**Review Fieberg et al. (2023) next.** It is freely available in full text and is a strong complement to Gu–Kelly–Xiu rather than a repetition: it studies nearly 12,000 stocks across 16 European economies, uses six predictors, and explicitly examines overfitting/irrelevant predictors, missing values, stock-size/liquidity sensitivity, and rolling estimation. It also includes SVR, which is in the Northgate PRD.

The next extraction should focus on:
- Exact universe construction, data sources and treatment of dead/delisted securities.
- Six predictors, definitions, timing and why the authors chose a sparse set.
- Missing values, scaling/ranking, outliers and any point-in-time safeguards.
- Exact rolling training/validation/test procedure and refit cadence.
- What happens as smaller firms are removed, and what the largest 10% result actually means.
- SVR, neural-network and tree-model settings, baselines and performance.
- Turnover, trading-cost assumptions and economic realism.
- What the European study still cannot tell us about a small Indian universe.

After that review, decide whether Chen–Pelger–Zhu is still needed for Phase 1 or whether it belongs in the later deep-learning model phase. Do not automatically process all five papers.

## Progress log

| Date | Progress | Current interpretation / next action |
|---|---|---|
| 2026-11-11 | Paper 1's three-page publisher landing-page printout reviewed; full article could not be obtained free. | Keep only abstract-level Indian-market context; do not pay for the article or treat its methodology as reviewed. |
| 2026-11-12 | Full-paper extraction for Gu–Kelly–Xiu reviewed. | Strong evidence on pooled cross-sectional modelling, monthly excess-return targets, feature timing, missing-data handling and chronological evaluation; small-universe and India transferability remain unresolved. |
| 2026-11-12 | Fieberg et al. full text confirmed open access. | Next source selected to test sparse-feature and robustness evidence across a non-US market. |

## Decisions

No dataset size, universe, target, horizon, feature set, model architecture, training window or recommendation rule is approved by this synthesis. Keep these as open research choices until the evidence is compared and the user explicitly confirms a decision.

# Research Synthesis & Progress — Northgate Stock Predictor

Updated: 2026-11-12

## Purpose

This is the **single rolling research document** for Northgate. It preserves cumulative, useful findings from reviewed sources, how evidence changes our understanding, what remains unresolved, and what we should investigate next.

Do not create separate paper-summary or teaching files. Keep source identities and review status for traceability, but continuously refine the synthesis below. Full extraction prompts and long raw notes stay in chat, not GitHub.

## Research discipline

- Use freely accessible full-text sources by default; do not make paid papers a required step.
- Distinguish source findings, our interpretation, and approved Northgate decisions.
- Record page, section, table, figure or appendix references for important claims.
- If a source does not state something, record **“Not stated in source.”**
- Do not transfer US/European findings directly to Indian equities without validation.
- Preserve contradictions and source limitations rather than silently resolving them.
- No finding becomes a project decision until discussed and explicitly approved.
- Keep the PRD scope intact unless the user approves a change.

## Sources reviewed / queued

| # | Source | Status | Why it matters |
|---|---|---|---|
| 1 | Lalwani & Meshram (2022), [The cross-section of Indian stock returns: evidence using machine learning](https://doi.org/10.1080/00036846.2021.1982132) | **Abstract/metadata only.** The available three-page file was a publisher landing-page printout, not the full article; full text was not found freely. | Limited India-specific context only. Its claimed survivorship-bias-free sample and one-month-ahead return study are not methodologically verified. |
| 2 | Gu, Kelly & Xiu (2020), [Empirical Asset Pricing via Machine Learning](https://doi.org/10.1093/rfs/hhaa009) — [free NBER PDF](https://www.nber.org/system/files/working_papers/w25398/w25398.pdf) | **Full-paper extraction reviewed.** The supplied extraction covered NBER Working Paper 25398 (December 2018; revised September 2019); this version should not be conflated with the final 2020 journal version without checking. | Large US cross-sectional panel; pooled learning; broad predictor design; time alignment; chronological evaluation; model and portfolio comparisons. |
| 3 | Fieberg et al. (2023), [Machine learning techniques for cross-sectional equity returns’ prediction](https://doi.org/10.1007/s00291-022-00693-w) — [free open-access full text](https://link.springer.com/article/10.1007/s00291-022-00693-w) | **Full paper reviewed** using the supplied source-only extraction. No separate supplementary-material file was available in the supplied project files. | European monthly firm-return panel; six predictors; universe/dead-list construction; missing-data and rank-normalisation choices; rolling validation; size/liquidity and portfolio results. |
| 4 | Chen, Pelger & Zhu (2024), [Deep Learning in Asset Pricing](https://doi.org/10.1287/mnsc.2023.4695) | Pending; review only if freely accessible full text/supplement is available. | Potentially useful later for the PRD's deep-learning model phase; not required to complete the current dataset-design comparison. |
| 5 | [Stock picking with machine learning](https://doi.org/10.1002/for.3021) | Optional; do not pursue unless full text is freely accessible and it fills a specific unresolved gap. | Possible additional stock-selection design; not required by default. |

## Cumulative research synthesis

This is an evidence synthesis, **not an approved Northgate specification**.

### 1. Prediction problem and learning structure

- Gu–Kelly–Xiu and Fieberg both study **cross-sectional stock-return prediction** using pooled firm-time observations: one common learned relationship produces predictions for many individual stocks.
- Fieberg's observation is a **firm-month**, with next-month return as target (Sections 2–3, pp. 293–295).
- Gu–Kelly–Xiu use a much broader US equity panel with stock characteristics and common macro information. Fieberg uses a European panel and six firm characteristics.
- Neither paper establishes that pooled learning is superior to per-stock models, because neither provides the controlled pooled-versus-individual comparison needed to answer that question.
- Neither establishes reliable pooled learning with only the PRD's 8–15 equities.
- Cross-sectional stock selection is not the same task as forecasting one index's time series. Northgate must clarify whether it intends one task or separate experiments.

### 2. Target and frequency

- Gu–Kelly–Xiu's supplied extraction reports next-month individual-stock **excess returns**, based on monthly total returns and a Treasury-bill risk-free adjustment.
- Fieberg predicts next-month individual-stock **returns** using monthly data and Datastream Total Return Index (RI) (Sections 3–4, pp. 295, 305–306). The paper does not explicitly establish whether its return calculation is simple or logarithmic or fully specify dividend/corporate-action mechanics.
- Lalwani & Meshram's abstract also mentions rolling one-month-ahead stock-return forecasts, but the full methodology is unavailable.
- These sources support monthly return prediction as a studied research design. They do **not** prove monthly is best for Northgate.
- The PRD currently describes daily OHLCV/adjusted-price data and daily/multi-day forward closing-price prediction. This is a material target/frequency mismatch with the two fully reviewed cross-sectional papers. Do not quietly replace the PRD target with monthly returns; explicitly reconcile the research task before modelling.
- Keep price, total return, excess return, directional classification and cross-sectional ranking distinct.

### 3. Predictors and feature design

- Gu–Kelly–Xiu's supplied extraction reports a broad baseline with 94 stock characteristics, 8 macro predictors and 74 industry indicators, resulting in 920 baseline covariates after interactions.
- Fieberg deliberately uses six established firm characteristics: beta, log market capitalisation, book-to-market, momentum, investment (asset growth), and operating profitability (Section 4, pp. 305–306).
- Fieberg's stated motivation is to test ML with a relatively sparse, established feature set rather than relying on hundreds of potentially irrelevant predictors (Introduction, pp. 290–292).
- These studies offer contrasting feature-design precedents: broad high-dimensional predictors versus a sparse six-characteristic set. They do not establish which is better for Northgate's daily Indian dataset.
- Fieberg's reported timing includes beta from the prior 12 months of daily returns, momentum from the prior 12-month total return excluding the latest month, and a six-month publication lag for accounting variables. The authors state this lag is assumed to avoid look-ahead bias (pp. 305–306).
- Feature availability, definitions, publication dates and historical point-in-time availability must be checked for India. Do not assume European/US accounting fields map cleanly to Indian sources.

### 4. Universe integrity and sample size

- Fieberg reports approximately 12,000 European stocks, January 1990–December 2019, monthly frequency, and about 1,755 observations per month (Section 4, pp. 304–306).
- It uses Datastream research, Worldscope and dead lists, removes duplicates, consolidates country lists and applies security/data screens (pp. 304–306).
- Important limitation: use of dead lists is documented, but complete historical coverage of every delisted/failed company is not established. The extraction also notes an inconsistency between the stated 16 economies and 15 countries named in a footnote.
- Fieberg progressively removes smaller stocks by market-cap quantiles; its largest-10% experiment still retains a segment of the original broad European universe. It is **not** a 10-stock or 8–15-stock experiment (Section 5.1, p. 307).
- In Fieberg's Table 2 (p. 307), full-universe versus largest-10% out-of-sample panel R² (percentage points) includes: OLS 0.43 vs -0.32; RF 0.58 vs -0.45; GBRT 0.60 vs 0.14; NN 0.67 vs 0.24. Only GBRT and NN remain positive in the largest-10% segment in the reported table.
- This demonstrates sensitivity to universe composition in that study; it does not prove that adding illiquid small stocks is suitable for Northgate. Northgate's PRD explicitly targets liquid large-cap equities, so liquidity and universe definition need their own India-specific evidence.
- Historical NSE/BSE membership, delisted firms, bankruptcies, symbol changes, corporate actions and survivorship bias remain unresolved.

### 5. Missing data and preprocessing

- Gu–Kelly–Xiu's supplied extraction reports monthly cross-sectional median imputation for missing characteristics and cross-sectional rank scaling to [-1, 1].
- Fieberg replaces missing characteristics with the cross-sectional median when a return observation exists, excludes observations with missing returns rather than imputing the target, and uses cross-sectional rank normalisation mapped to [-1, 1] (pp. 306–307).
- Fieberg says this helps address differing scales and extreme observations; the exact ranking formula and tie handling are not specified. Separate winsorisation and z-score procedures are also not specified.
- This is a useful point of convergence: cross-sectional median treatment and rank-based normalisation appear in both supplied study extractions. It is not enough to conclude they are automatically safe or optimal for Northgate.
- Fieberg does not provide a complete audit proving every preprocessing statistic uses only information available at the prediction timestamp. Northgate must explicitly test and document point-in-time fitting and prevent cross-period leakage.

### 6. Training and validation

- Gu–Kelly–Xiu's supplied extraction describes chronological training/validation/test, expanding training history, rolling 12-year validation and annual refitting.
- Fieberg uses a **10-year rolling estimation window**, split into 7 years of training and 3 years of validation; it selects hyperparameters, re-estimates on the full 10 years, forecasts the subsequent year and rolls forward (Section 3.5, pp. 302–304, Figure 4).
- Fieberg states forecast-period data do not enter estimation. It does not describe purging overlapping labels. The extraction notes inconsistent test-period dates: January 2001–December 2019 on p. 304 versus January 2000–December 2019 in some table notes.
- Both studies support chronological validation rather than random shuffling. Their exact windows differ and are designed for long historical panels; neither establishes an optimal window for Northgate's 8–10-year history.
- Preserve the general safeguards: validation/tuning must precede the untouched final test; feature availability must be time-aligned; fit transformations only on information available in each training period; consider purging overlapping forward labels where relevant.

### 7. Model comparisons and complexity

- Gu–Kelly–Xiu compare linear/regularised, dimension-reduction, tree-based and feed-forward neural-network models. Their supplied extraction reports NN3 (three hidden layers: 32, 16 and 8 neurons) outperforming deeper NN4/NN5 variants in their main stock-level comparison.
- Fieberg compares OLS, Lasso, Ridge, Elastic Net, RBF-kernel SVR, Random Forest, gradient-boosted regression trees (GBRT), and a feed-forward neural network (Sections 3.1–3.5, pp. 295–303).
- Fieberg's NN is not an LSTM, GRU, BiLSTM or Transformer: it has one hidden layer with 12 neurons, tanh activation, Adam, L2 weight decay, early stopping and an average of ten networks (pp. 302–303; Table 11, p. 320).
- In Fieberg's full-universe Table 2 (p. 307), RF, GBRT and NN outperform OLS on its reported panel R²; SVR is sensitive to hyperparameters and performs poorly on that predictive metric. The paper's results are specific to its monthly European panel and six predictors.
- The two studies justify testing nonlinear models against simple linear baselines; they do not prove deep learning always wins or transfer to a small Indian sample.
- The PRD's required architectures still need separate evidence and fair experiments on the same Northgate data, dates, target and baselines.

### 8. Predictive accuracy versus economic performance

- Both studies reinforce that forecast accuracy and portfolio outcomes are separate evaluation layers.
- Fieberg forms ten forecast-sorted deciles and evaluates a zero-net-investment long–short strategy: buy the highest predicted-return decile and short the lowest (Section 6.1, pp. 313–314).
- In its full-universe Table 4 (pp. 309–310), RF has the highest reported average monthly high-minus-low return (2.38%), while GBRT has the highest reported monthly Sharpe (0.56; annualised Sharpe 1.94 as reported). These are historical results from the authors' European long–short experiment, not Northgate expectations.
- Fieberg reports monthly turnover of 124–154% across models (Table 6, p. 314). It explicitly discusses difficulty estimating realistic transaction costs; complete profitability after brokerage, spread, taxes, market impact and slippage is not established.
- Fieberg also finds predictive R² and long–short portfolio outcomes need not rank models identically; SVR is a useful example (pp. 307–313).
- Gu–Kelly–Xiu's supplied extraction also reports portfolio results sensitive to micro-cap inclusion. Do not use either paper's Sharpe/return as a project target.
- Northgate must evaluate forecast error, directional accuracy, BUY/HOLD/SELL outcomes and capital-weighted portfolio performance separately, with Indian costs, turnover, liquidity and benchmarks.

## What the reviewed evidence does NOT establish

| Question | Current evidence |
|---|---|
| Minimum number of stocks needed | Not stated by either fully reviewed paper. |
| Reliable performance with 8–15 stocks | Not tested/established. |
| Pooled versus per-stock superiority | Neither provides the required controlled comparison. |
| Indian-market transferability | Not established by the two international studies; Paper 1 is only abstract-level. |
| Daily versus monthly superiority | Not compared in a way that answers Northgate's question. |
| Optimal Northgate target/horizon | Not established. |
| Universally optimal feature set | Not established; studies use different feature sets and markets. |
| Universally optimal training window | Not established. |
| Complete delisted-company coverage | Not established for Fieberg from the supplied extraction. |
| Fully realistic transaction-cost-adjusted profitability | Not established by Fieberg's reported analysis. |
| LSTM/GRU/BiLSTM/Transformer superiority | Not established by Fieberg. |
| Incremental value of news sentiment | Not established by these papers. |
| BUY/HOLD/SELL effectiveness | Not established. |
| Mean-variance optimisation benefit for Northgate | Not established. |

## Current interpretation for Northgate — provisional, not decisions

1. **Do not confuse the PRD's current daily forward-price task with the monthly cross-sectional return task in these papers.** This is the most important unresolved design issue to clarify.
2. A pooled panel is a credible candidate to test, but the literature reviewed so far does not answer whether it works with only 8–15 companies. We should not claim that it does.
3. Feature count alone is not a quality measure. A broad predictor set and a sparse established set are both studied; the relevant Northgate test is availability, timing, leakage control and incremental out-of-sample value.
4. Cross-sectional median imputation and rank scaling are methods worth testing, not defaults to adopt without checking missingness, time alignment and leakage.
5. Model selection must account for the universe: Fieberg's size-segment results show performance can change when small firms are excluded, but do not imply we should add illiquid firms.
6. Strong forecast metrics do not prove tradable performance. Turnover and realistic Indian trading costs need explicit modelling.
7. Keep the PRD's required models visible. Neither study's feed-forward neural network is evidence that the PRD's recurrent/Transformer architectures have been validated.

## Open questions to resolve

1. Is Northgate's primary task daily/multi-day price forecasting, return prediction, cross-sectional ranking, or separate experiments for more than one?
2. What does the PRD mean precisely by “forward closing prices”: which forecast horizons, signal time and execution convention?
3. Can pooled learning be evaluated fairly with the PRD's 8–15 equities, and should a simple per-stock baseline be included?
4. Which Indian-market features are available reliably with point-in-time publication dates?
5. Can we obtain historical NSE/BSE membership, delisted securities and corporate-action-adjusted returns?
6. Is daily data sufficient for the chosen target, or should a separate monthly cross-sectional experiment be treated as a distinct task?
7. Which preprocessing methods can be fitted without cross-sectional or temporal leakage?
8. Which model families are feasible with the available sample size, compute and deadline?
9. What realistic Indian brokerage, statutory charges, spread, slippage, market impact, liquidity and turnover assumptions should be used?
10. Does news/sentiment add incremental value beyond price/volume features on identical out-of-sample dates?

## Next research step

**Do cross-paper synthesis now; do not automatically process another dataset paper.** Gu–Kelly–Xiu and Fieberg provide a useful contrast in universe size, feature breadth, preprocessing, model comparisons and evaluation. The next work should clarify the Northgate prediction task against the PRD and decide which gaps genuinely need further evidence.

Defer Chen–Pelger–Zhu until the deep-learning/model-comparison phase unless a specific unresolved dataset question requires it. The optional stock-picking paper is not required at present. The India-specific paper remains a possible gap, but its full text is not freely available; do not pay for it by default.

## Progress log

| Date | Progress | Current interpretation / next action |
|---|---|---|
| 2026-11-11 | Paper 1's three-page publisher landing-page printout reviewed; full article could not be obtained freely. | Retain abstract-level India context only; its methodology remains unverified. |
| 2026-11-12 | Gu–Kelly–Xiu full-paper extraction reviewed. | Evidence on pooled cross-sectional modelling, monthly excess-return targets, feature timing, missing-data handling and chronological evaluation; small-universe and India transferability remain unresolved. |
| 2026-11-12 | Fieberg et al. (2023) full-paper extraction reviewed from the uploaded source-only analysis. | Evidence on a monthly pooled European panel, six firm characteristics, dead-list construction, median imputation/rank scaling, 10-year rolling estimation, model comparisons, size sensitivity, turnover and long–short evaluation. Important limits: no 8–15-stock test, no India test, and no complete realistic cost model. |

## Decisions

No dataset size, universe, target, horizon, feature set, model architecture, training window, preprocessing method or recommendation rule is approved by this synthesis. Keep these as open research choices until discussed and explicitly confirmed.


## Official PLFS release and MCP coverage update (reviewed 2026-11-13)

### Source evidence
- The official NSO India [e-Sankhyiki MCP repository](https://github.com/nso-india/esankhyiki-mcp) documents the ordered tool workflow `list_datasets → get_indicators → get_metadata → get_data` and the hosted endpoint `https://mcp.mospi.gov.in/`. Its current PLFS tool documentation states that monthly frequency (code 3) covers April 2025–September 2026 for All India and indicators 1–3; quarterly frequency (code 2) covers calendar years 2018–2026 for indicators 1–4, with uneven quarter availability. These are API metadata claims; no observations were fetched in this review.
- The official [MoSPI July–September 2026 PLFS Quarterly Bulletin](https://www.mospi.gov.in/uploads/publications_reports/publications_reports1794297172776_05eae330-7f2d-45ec-84c5-07031201ecf1_PLFS_QB_July-Sept_2026_m.pdf) is dated 10 November 2026. It reports LFPR, WPR, UR and worker distributions in Current Weekly Status (CWS), separately for rural, urban and combined India.
- The bulletin states that the April–June 2025 quarterly bulletin was the first to extend quarterly estimates to rural and urban India; earlier quarterly bulletins through December 2024 were urban-only. This creates a comparability break in geography/coverage for the quarterly series, separate from any change in survey methodology.

### Interpretation and Northgate handling
- Do not call the September 2026 release a “monthly bulletin”. It is the latest quarterly bulletin; September 2026 is also the endpoint stated for the monthly API series. Keep monthly API records and quarterly bulletin records in separate tables.
- Do not infer the monthly indicator's CWS definition from the quarterly bulletin or from an annual-only weekly-status filter. Retain the exact indicator definition returned by MCP metadata.
- For quarterly CWS data, preserve the 2025 Q1 rural-coverage expansion as a coverage-break flag. For the monthly data, preserve the post-April-2025 series start and its own official metadata.
- Publication date is distinct from reference month. The latest quarterly PDF is dated 10 November 2026; use the actual release date for availability, not quarter-end.
- This evidence supports source feasibility and data-contract design only. No PLFS values have been downloaded, checked, or merged, and no macro feature is yet validated point-in-time.

### Next research/implementation action
Execute the official MCP sequence against the hosted service, capture raw responses and metadata, then build separate monthly and quarterly PLFS raw tables with explicit reference period, frequency, indicator definition, geography, status concept, publication date, source URL and retrieval timestamp. Test completeness and duplicate keys before creating any market-session-aligned feature.


## 2026-11-13 — PLFS release-calendar and official export workflow correction

The MoSPI 2026–27 Advance Release Calendar updated through October 2026 clarifies a previously incomplete PLFS timeline:
- Monthly PLFS September 2026 bulletin: released 15 October 2026 (PIB PRID 2323828).
- Quarterly PLFS July–September 2026 bulletin: dated 10 November 2026.
- Monthly PLFS October 2026 bulletin: scheduled 15 November 2026, so it was not yet due on the review date 13 November.
Thus monthly and quarterly bulletins are parallel products. The monthly API coverage through September 2026 is a third, distinct data-access statement. Retain each product/frequency and its actual publication date independently. Advance calendar dates are schedules, not guaranteed actual timestamps.

Official export paths were rechecked:
- NSE Historical Data – India VIX exposes a date-range selection and CSV download. An unfiltered page can display No Records; set a valid range before concluding there is no data. NSE's Historical Reports page also lists VIX, historical index, TRI and index-report archives. Official source is preferred, but no file has been retrieved.
- RBI DBIE Key Rates table financial_sector.r531_key_rates visibly offers CSV/JSON export and reports 271 effective-date rows through 7 October 2026. The export is now considered manually accessible; automated retrieval is not yet implemented. Keep event dates and forward-fill only after each effective date.
- NSE filings are a candidate source of timestamped regulatory disclosures, but third-party descriptions of broadcast/dissemination timestamps are not an official API contract. Treat filings separately from editorial news and do not use paid scraping without approval.

No observations were downloaded in this pass. Next practical retrieval sequence: export RBI DBIE CSV; export NSE VIX in manageable annual/custom date ranges; use the official MoSPI MCP workflow (list_datasets → get_indicators → get_metadata → get_data) to retrieve monthly PLFS indicator metadata and observations; then investigate NSE/BSE filing access/terms for a timestamped event dataset.


## 2026-11-13 — PLFS metadata and NSE timestamp discovery update

The official e-Sankhyiki catalogue explicitly defines the monthly PLFS LFPR, WPR and UR records as **Current Weekly Status (CWS)**. September 2026 catalogue entries have reference month Sep 2026, release date 15 October 2026 and table IDs PLFSFY26001SEP, PLFSFY26002SEP and PLFSFY26003SEP. This corrects the earlier caution in the project notes: the annual-only `weekly_status_code` API filter must not be confused with the published monthly product's CWS definition. For MCP retrieval, request metadata for each indicator separately with `frequency_code=3`, then use returned filter values for `get_data`; do not pass annual-only filters into monthly calls.

A new structural break is approaching. PIB's 23 October 2026 notice describes PLFS sampling and schedule changes proposed from January 2027, including a digital-platform-worker stratum, refreshed Panel 6 sample frame, and a three-month transition combining Panel 5 and Panel 6 FSUs. Monthly estimates for those three months are planned to be pooled, with no RSE estimates. Since the note invited comments on proposed changes, check final implementation documentation when released. Flag January 2027 onward and avoid unqualified splicing.

NSE Corporate Filings Summary Documents exposes company/subject/date filters, CSV download and `BROADCAST DATE/TIME`. A displayed example records broadcast at 19-Sep-2026 14:47:29 and exchange dissemination at 14:47:34 (five seconds later). This is promising direct evidence for timestamped regulatory events. Validate the main announcements archive's historical depth, categories, CSV schema and attachment access before adopting it. It is not a replacement for editorial news.

No raw PLFS, VIX, RBI or NSE filing data have been downloaded. This is source metadata and timestamp-contract research only. Sources: official e-Sankhyiki catalogue; NSO MCP implementation; PIB 23-Oct-2026 PLFS change notice; NSE Corporate Filings Summary Documents page.

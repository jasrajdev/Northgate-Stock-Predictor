# Research Roadmap — Northgate Stock Predictor

Updated: 2026-11-11  
Status: Phase 1 source pack prepared; no paper findings have yet been accepted as project decisions.

## Purpose and research rules

This document tracks the specific knowledge gaps that must be answered from the PRD before Northgate's data, models, and evaluation design are finalised. It is a living research register: add source-grounded findings, limitations, unresolved questions, and decisions as research is completed. Do not turn a paper's result into a Northgate decision without checking its setting and transferability to Indian equities.

### Non-negotiable source discipline

> 🚨🚨🚨 **TRIPLE-HIGHLIGHTED RULE — SOURCE-ONLY EXTRACTION.** Each source prompt below authorises the research assistant to use ONLY the named paper/source. Do not use general knowledge, other papers, web searches, prior chat context, or assumptions to fill gaps. If the source does not state something, write **“NOT STATED IN THIS SOURCE.”** If the source cannot be accessed in full, say exactly which parts were inaccessible and limit extraction to visible material. Every substantive claim must carry a page, section, table, figure, equation, or appendix reference. Never invent sample sizes, definitions, results, data availability, or recommendations.

Additional rules:
1. Separate **source facts**, **authors' interpretations**, and **our unanswered Northgate questions**.
2. Do not convert correlation or predictive association into causation.
3. Do not generalise US/European findings to India without an explicit external-validity caveat.
4. Do not treat the number of stock-date rows as the number of independent observations.
5. Do not propose a final company count, split ratio, target, feature set, or training design unless the source directly supports it. Otherwise record it as unresolved.
6. A source prompt is an extraction task, not permission to research the question independently.

## PRD requirements that Phase 1 must resolve

The uploaded PRD specifies:
- A universe of **8–15 liquid, large-cap equities** plus one broad-market index.
- At least **8–10 years of daily data**.
- Daily OHLCV and adjusted-close information; adjusted series must be used for return and target calculations.
- Market indices and macroeconomic indicators.
- Forecasting **next-day and multi-day forward closing prices** (Section 2); Section 3.1 emphasises adjusted prices for return and target calculations. The exact target definition needs to be reconciled explicitly rather than assumed.
- A company-level and broad-market textual/news dataset with timestamps.
- Cross-sectional and time-series features, then classical ML and deep-learning model comparisons.

Phase 1 is only about **what observations, companies, dates, targets, and predictor data should enter the training dataset**. Training mechanics (epochs, batches, sequence lengths, validation implementation) belong to Phase 2. Model architecture comparisons belong to Phase 3. Do not drift into those phases while extracting Phase 1 papers.

## Research workstreams

| ID | Specific research question | Required output | Status |
|---|---|---|---|
| P1.1 | Should Northgate learn one pooled relationship across stocks, one model per stock, or a hybrid? What does cross-sectional versus single-series forecasting mean in the papers? | Evidence table of study design, panel structure, model unit, and limits for a 8–15-stock universe | In progress |
| P1.2 | What does the literature actually use for number of firms, date coverage, and observation frequency? | Comparable study table; no universal minimum unless directly established | In progress |
| P1.3 | What universe construction avoids survivorship and selection bias? | Point-in-time universe requirements and Indian-market evidence | In progress |
| P1.4 | What target is modelled: raw price, adjusted price, simple/log return, excess return, or relative/outperformance label? At what horizon/frequency? | Source-by-source target definition and unresolved PRD interpretation | In progress |
| P1.5 | Which predictor families are supported by evidence, and at what data frequency are they available? | Feature inventory with source, frequency, lag/availability rule, missingness, and limitations | In progress |
| P1.6 | What is the evidence on missing characteristics, imputation, and sparse versus large feature sets? | Missing-data policy options grounded in sources; no blanket imputation rule | In progress |
| P1.7 | What dataset dimensions and computational constraints are reported in relevant studies? | Row counts, number of firms, dates, features, frequency, memory/runtime where stated | In progress |

## Phase 1 — source pack and source-specific prompts

Read the sources in the order below. Start with the Indian study, then compare it with the larger international studies. These papers answer different questions; none alone establishes the correct Northgate universe size.

### Source 1 — Indian equity cross-section (highest relevance)

**Vaibhav Lalwani & Vedprakash Vasantrao Meshram (2022), “The cross-section of Indian stock returns: evidence using machine learning.” Applied Economics, 54(16), 1814–1828.**

- DOI / article: https://doi.org/10.1080/00036846.2021.1982132
- Publisher page: https://www.tandfonline.com/doi/full/10.1080/00036846.2021.1982132
- Visible abstract states: 35 stock characteristics; a survivorship-bias-free sample of firms listed on major Indian exchanges from 1994–2019; rolling one-month-ahead out-of-sample return forecasts; OLS compared with machine-learning methods.
- Access note: the publisher may require institutional access. Do not pretend the abstract is the full paper.

**Copy/paste prompt**

You are extracting evidence from ONE source only:

“ The cross-section of Indian stock returns: evidence using machine learning ” by Vaibhav Lalwani and Vedprakash Vasantrao Meshram (2022), DOI 10.1080/00036846.2021.1982132.

🚨🚨🚨 **TRIPLE-HIGHLIGHTED SOURCE RULE: USE ONLY THIS PAPER AND ITS OWN APPENDIX/SUPPLEMENTARY MATERIAL, IF PROVIDED. DO NOT use your pretrained knowledge, other papers, websites, search results, or assumptions. Do not independently answer questions the paper does not answer. If a fact is absent or inaccessible, write “NOT STATED IN THIS SOURCE” or “NOT ACCESSIBLE IN THE PROVIDED SOURCE.”**

Extract ONLY the following:
1. **Universe construction:** exact exchanges, security types, inclusion/exclusion criteria, date-by-date or point-in-time universe method, treatment of delisted firms, and how the authors establish that the sample is survivorship-bias-free. Quote the exact description and cite page/section/table.
2. **Number of companies and observations:** exact number of firms, total firm-period observations if reported, start/end dates, frequency, missing observations, and whether counts vary over time. Do not estimate missing counts.
3. **Target:** exact dependent variable definition, price versus return, adjusted/raw basis if specified, excess versus total return, forecast horizon, and target timing.
4. **Predictors:** list all 35 characteristics exactly as named; classify only as the paper classifies them. Record their calculation/measurement timing and any lags or publication delays stated.
5. **Model structure:** explain whether the model is pooled across firms, estimated separately per firm, or uses another structure. State how the cross-section is formed at each prediction date.
6. **Forecast design:** exact rolling/expanding window, training period, validation/tuning process, retraining frequency, and out-of-sample dates.
7. **Missing data and preprocessing:** exact treatment of missing values, scaling/ranking, outliers, and any transformations.
8. **Reported findings relevant to dataset design:** only results that directly compare sample construction, predictor groups, universe breadth, or forecast target/frequency.
9. **Limitations acknowledged by the authors:** reproduce the authors' own caveats, not your own speculation.

Return:
A. A structured extraction table with columns: Question | Exact source finding | Page/section/table | Exact quote (short) | Not stated / access limitation.
B. A final section titled “What this paper does NOT establish” listing every requested Northgate question the paper cannot answer.
C. A section titled “Northgate follow-up questions” containing questions only—no answers or recommendations.

Do not recommend a number of Northgate stocks from this paper unless the authors explicitly test and justify that number. Do not claim the Indian results will transfer to Northgate's 8–15 large-cap stocks unless the paper tests that exact setting.

### Source 2 — Large-scale machine-learning asset pricing benchmark

**Shihao Gu, Bryan Kelly & Dacheng Xiu (2020), “Empirical Asset Pricing via Machine Learning.” Review of Financial Studies, 33(5), 2223–2273.**

- Open journal article: https://academic.oup.com/rfs/article/33/5/2223/5758276
- Free NBER working-paper PDF: https://www.nber.org/system/files/working_papers/w25398/w25398.pdf
- DOI: https://doi.org/10.1093/rfs/hhaa009
- Paper setting (for orientation only): US equities, CRSP, nearly 30,000 stocks over 1957–2016, monthly returns, 94 stock characteristics, macro interactions and industry indicators. These figures must be verified and extracted from the paper itself.

**Copy/paste prompt**

You are extracting evidence from ONE source only:

Gu, Kelly & Xiu (2020), “Empirical Asset Pricing via Machine Learning,” Review of Financial Studies. Use the linked published paper and its own Internet Appendix only.

🚨🚨🚨 **TRIPLE-HIGHLIGHTED SOURCE RULE: DO NOT use any external source, general finance knowledge, pretrained assumptions, or other paper to fill gaps. If the paper does not state a requested item, write “NOT STATED IN THIS SOURCE.” Cite the exact page, section, table, figure, equation, or Internet Appendix location for every factual claim.**

Extract ONLY:
1. **Panel dimensions:** number of stocks, exchanges, date range, observation frequency, total or average stock-period observations if stated, and any sample filters.
2. **Learning unit:** is the prediction function estimated across the stock cross-section, through time for an aggregate index, or both? Identify the exact dependent variable and model notation.
3. **Target construction:** define the individual-stock target and aggregate-market target separately; state whether returns are total/excess, monthly/daily, and the forecast horizon.
4. **Universe logic:** explain how firms enter/leave the sample and what the paper says about microcaps, financial firms, delisted stocks, share codes, or survivorship, if anything.
5. **Predictor inventory:** identify the 94 characteristics, eight macro predictors, industry dummies and interaction construction. Do not reproduce a list unless it is actually in the paper or appendix; identify the exact appendix table.
6. **Predictor availability:** extract the publication lags used for monthly, quarterly and annual characteristics. Explain the exact timing convention and why it is used, using the authors' wording.
7. **Missing values:** exact imputation method and cross-sectional/time treatment.
8. **Sample split:** exact training, validation and out-of-sample periods; retraining frequency; whether windows expand or roll.
9. **Dataset scale and computation:** any stated row counts, predictor counts, memory/runtime or computational constraints.
10. **Relevant results:** findings that bear directly on whether a broad cross-section, predictor interactions, or a large feature set is useful. Include the relevant sample context and limitations.

Return:
A. Exact dataset specification as used by the paper.
B. Exact target and predictor specification.
C. Exact train/validation/test timeline.
D. A table separating “paper explicitly states” from “not stated.”
E. “Transferability limits for Northgate” — list differences between this US monthly all-stock study and an Indian 8–15-stock daily project. Do not resolve those differences using outside knowledge.

Do not treat the paper's large sample as proof that Northgate must use the same number of stocks. Do not claim a minimum sample size unless the authors explicitly estimate one.

### Source 3 — European cross-section; sparse predictors and missing-data robustness

**Christian Fieberg, Daniel Metko, Thorsten Poddig & Thomas Loy (2023), “Machine learning techniques for cross-sectional equity returns’ prediction.” OR Spectrum, 45, 289–323.**

- Open-access publisher page (includes PDF): https://link.springer.com/article/10.1007/s00291-022-00693-w
- DOI: https://doi.org/10.1007/s00291-022-00693-w

**Copy/paste prompt**

You are extracting evidence from ONE source only:

Fieberg et al. (2023), “Machine learning techniques for cross-sectional equity returns’ prediction,” OR Spectrum.

🚨🚨🚨 **TRIPLE-HIGHLIGHTED SOURCE RULE: USE ONLY THIS ARTICLE AND ITS OWN APPENDIX/SUPPLEMENT. No external sources, pretrained knowledge, general assumptions, or invented explanations. If the paper does not report a detail, write “NOT STATED IN THIS SOURCE.” Cite page/section/table/figure for each claim.**

Extract ONLY:
1. **Sample size and universe:** exact number of firms, countries, exchanges/markets, date range, frequency, and sample-selection criteria.
2. **Target and prediction horizon:** exact return definition, frequency, forecast timing and whether it is a cross-sectional ranking or absolute return prediction.
3. **Model unit:** exact pooled/cross-sectional model design and how firms are compared at each date.
4. **Predictor design:** list the exact six predictor variables used in the sparse specification; identify their definitions, source timing and transformations as stated.
5. **Missingness:** how the authors select predictors with broad availability; what they say about missing data and when imputation may be inappropriate. Extract any explicit thresholds or citations only as the authors present them.
6. **Overfitting control:** what design choices are used to control irrelevant predictors and overfitting.
7. **Universe breadth test:** extract the comparison involving the largest 10% of firms. State precisely how that subset is defined and what changes in the results; do not generalise beyond the paper's test.
8. **External validity:** extract the authors' discussion of US bias and the reason for testing European firms.
9. **Northgate relevance:** state only the methodological questions this paper helps frame. Do not prescribe an Indian stock count or claim its results will replicate in India.

Return:
A. A data-design table.
B. A predictor table.
C. A missing-data/overfitting table.
D. A precise “what the paper cannot tell Northgate” list.
E. All citations must identify page/section/table.

Do not turn the paper's 12,000-stock sample into a minimum stock-count recommendation.

### Source 4 — Deep-learning asset-pricing dataset structure (supplementary)

**Luyang Chen, Markus Pelger & Jason Zhu (2024), “Deep Learning in Asset Pricing.” Management Science, 70(2), 714–750.**

- Publisher page and supplemental material: https://pubsonline.informs.org/doi/10.1287/mnsc.2023.4695
- DOI: https://doi.org/10.1287/mnsc.2023.4695
- Authors' data/code page: https://mpelger.people.stanford.edu/data-and-code

**Copy/paste prompt**

You are extracting evidence from ONE source only:

Chen, Pelger & Zhu (2024), “Deep Learning in Asset Pricing,” Management Science, including only its own supplementary material/data documentation if accessible.

🚨🚨🚨 **TRIPLE-HIGHLIGHTED SOURCE RULE: DO NOT supplement with other papers, websites, pretrained knowledge, or assumptions. If something is not explicitly in this paper or its own supplement, write “NOT STATED IN THIS SOURCE.” Cite exact page/section/table/appendix.**

Extract ONLY:
1. The exact assets, firms, date range, data frequency and number of observations used.
2. The exact return/target definitions and prediction horizon(s).
3. The exact firm-level characteristics and macroeconomic input categories used; distinguish raw variables from constructed features.
4. How time variation and macroeconomic states enter the data design.
5. Any missing-data, scaling, normalisation, publication-lag or point-in-time rules explicitly described.
6. How the data is split for out-of-sample evaluation, including dates and retraining protocol.
7. What parts of the data design are essential to the authors' method and what parts are specific to their research question.
8. Any stated data/code availability constraints.

Return a source-grounded dataset map and a “not stated / not transferable” section. Do not explain how to implement a Transformer or LSTM unless the paper's dataset section directly requires that detail. Do not infer that this model is appropriate for Northgate merely because it uses deep learning.

### Source 5 — Small(er) universe with a pooled weekly panel (optional comparison)

**“Stock picking with machine learning.” Forecasting journal article, DOI: 10.1002/for.3021.**

- Publisher page: https://onlinelibrary.wiley.com/doi/10.1002/for.3021

**Access warning:** use this only if the full paper is accessible. Search-result snippets are not sufficient for a full extraction.

**Copy/paste prompt**

You are extracting evidence from ONE source only:

“Stock picking with machine learning,” DOI 10.1002/for.3021. Use the full article and its own supplement only.

🚨🚨🚨 **TRIPLE-HIGHLIGHTED SOURCE RULE: SOURCE-ONLY. Do not use search snippets, general knowledge, other papers, or assumptions. If the full paper is inaccessible, stop and report that; do not reconstruct it from abstracts or snippets.**

Extract ONLY:
1. Exact universe and historical constituent handling.
2. Exact number of firms and weekly observations per training period.
3. Exact reason the authors give for combining cross-sectional stock data with weekly time-series observations.
4. Exact target label and forecast horizon.
5. Exact rolling training-window length, validation fraction, retraining schedule and test period.
6. Exact feature families and missing-data/scaling procedures.
7. Exact limits and caveats acknowledged by the authors.

Return a table with source citations and a separate “not established by this paper” list. Do not assume its three-year/500-stock design is optimal for Northgate.

## Phase 1 synthesis template

After each source has been analysed, paste its extraction into the project research conversation. Consolidate findings here using this table; do not copy unverified conclusions into the decisions log.

| Decision area | Evidence from Indian paper | Evidence from Gu et al. | Evidence from Fieberg et al. | Evidence from Chen et al. | Northgate conclusion | Confidence / unresolved issue |
|---|---|---|---|---|---|---|
| Pooled vs per-stock model | Pending | Pending | Pending | Pending | Pending | Pending |
| Number of firms / breadth | Pending | Pending | Pending | Pending | Pending | Pending |
| Historical duration | Pending | Pending | Pending | Pending | Pending | Pending |
| Daily vs weekly vs monthly | Pending | Pending | Pending | Pending | Pending | Pending |
| Price vs return target | Pending | Pending | Pending | Pending | Pending | Pending |
| Forecast horizon | Pending | Pending | Pending | Pending | Pending | Pending |
| Universe / survivorship | Pending | Pending | Pending | Pending | Pending | Pending |
| Feature families | Pending | Pending | Pending | Pending | Pending | Pending |
| Feature availability lags | Pending | Pending | Pending | Pending | Pending | Pending |
| Missing data | Pending | Pending | Pending | Pending | Pending | Pending |

### Phase 1 completion gate

Phase 1 is complete only when we can state, with traceable evidence or explicitly labelled unresolved items:
- the proposed universe construction and whether point-in-time membership is feasible;
- whether Northgate should use pooled, per-stock, or comparative model designs;
- the dataset frequency and historical duration to pilot;
- exact forecast target(s) and horizons, including resolution of the PRD's price/adjusted-price wording;
- the candidate predictor families and their point-in-time availability requirements;
- missing-data and survivorship limitations;
- the pilot dataset's expected dimensions and what evidence supports them.

No final stock count or target is pre-approved by this document. Any proposed PRD change must be presented to the user for approval before being recorded as a decision.

## Later research phases (scope register)

These are planned research areas, not yet source-packed. Add specific sources and source-only prompts when each phase begins.

### Phase 2 — Training and validation mechanics
- Chronological train/validation/test design and walk-forward evaluation.
- Purging/embargo where forward labels overlap.
- Lookback windows, sequence construction and boundary handling.
- Batches, epochs, learning curves, early stopping and regularisation.
- Hyperparameter tuning without contaminating the final test set.

### Phase 3 — Prediction models
- Linear/Ridge, Random Forest, XGBoost and SVR: suitable data structures, assumptions, tuning and failure modes.
- LSTM, GRU, BiLSTM and Transformer: data requirements, sequence design, compute and evidence of incremental value.
- Simple baselines and model-comparison fairness.

### Phase 4 — Financial features and statistical tests
- Technical indicators and redundant feature families.
- Returns, stationarity, ADF interpretation, volatility, beta and regime features.
- Feature selection, scaling, missingness and point-in-time fundamental/macro data.

### Phase 5 — News and sentiment
- Deployable hosted inference versus APIs; no requirement that the user's laptop run continuously.
- Financial-news models and reusable GitHub repositories.
- Official company filings, timestamped news access, deduplication and historical coverage.
- Optional public investor sentiment (forums/social sources): data access, API terms, representativeness and noise.
- Whether sentiment adds out-of-sample value beyond price/volume features.

### Phase 6 — Decision and risk methods
- BUY/HOLD/SELL rule design and evaluation.
- Stop-loss, trailing stop, holding-period and transaction-cost research.
- Portfolio optimisation, robust covariance/expected-return estimation and risk constraints.

### Phase 7 — Practical system design and delivery
- Scheduled/cloud deployment, hosted data jobs and inference.
- Cost, reliability, monitoring and reproducibility.
- Dashboard, report and acceptance-test design.

## Research log

Append dated entries here as papers are actually reviewed. Each entry must include source, sections reviewed, verified findings, inaccessible sections, unresolved questions, and whether any decision was explicitly approved. Do not mark a source complete based on its abstract alone.

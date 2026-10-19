# Project Notebook

## Research question
Can machine learning discover a useful signal in stock-market data that improves investment decisions out of sample?

## Required scope from Northgate PRD
- 8–15 liquid large-cap equities plus a market benchmark; roughly 8–10 years of daily OHLCV and adjusted-close data, relevant macro series, and timestamped financial news.
- EDA and finance math; compare 4 classical ML models (Linear/Ridge, Random Forest, XGBoost, SVR) and 4 deep-learning models (LSTM, GRU, BiLSTM, Transformer).
- Test FinBERT/VADER sentiment impact; mean-variance portfolio optimization; backtesting, risk metrics, recommendation logic, and a 7-panel Streamlit dashboard.
- Deliver reproducible code, comparisons, dashboard, and a 10–15 page report. Check the original PRD for exact requirements before finalizing.

## Current research direction — 2026-10-19
- Market focus selected by user: Indian equities, because the system should be relevant to their own market use.
- Specific stocks, benchmark, prediction target/horizon, macro variables, and news sources are not selected yet.
- Before full collection, review research papers and official source documentation to make data and feature choices evidence-led.
- The user proposed looking beyond company news: government policies, RBI decisions, macroeconomic changes, global events, and market-wide news can affect companies or sectors. Preserve this as a core research hypothesis.
- Candidate news pipeline: collect timestamped items; classify topic/event; identify affected company/sector where possible; estimate sentiment; deduplicate; align to information availability; test whether each feature group adds out-of-sample value.
- Candidate event-study idea: for large price/volume moves, retrieve events known at the time as plausible explanations. This is explanatory research, not proof of causality.
- Avoid prematurely building multiple agents or training a new language model. First establish a simple baseline and evaluate whether the added complexity helps.

## Research leads (not yet fully reviewed)
- Dasgupta et al., “Understanding the Impact of News Articles on the Movement of Market Index: A Case on Nifty 50” (arXiv:2412.06794): India/Nifty-focused study examining news topic sentiment beyond company-specific stories. Need to review its methodology, data, and limitations before adopting anything.
- Saqur et al., “NIFTY Financial News Headlines Dataset” (arXiv:2405.09747): a practical example of news collection, relevance filtering, deduplication, topic ranking, and pairing news with market observations. Its market data is US-equity-oriented, so treat it as a methodological reference rather than an Indian dataset.
- Tetlock (2007), “Giving Content to Investor Sentiment: The Role of Media in the Stock Market”: foundational evidence on media pessimism and market behavior; not India-specific.
- Araci (2019), “FinBERT: Financial Sentiment Analysis with Pre-trained Language Models”: background on finance-specific sentiment models; sentiment classification alone does not prove forecasting value.
- Official source candidates: NSE reports/bhavcopy for exchange data and RBI DBIE for Indian economic/financial time series. Access, historical coverage, licensing, and timestamps must be checked.

## Non-negotiable research safeguards
- Split data by time, never randomly across dates.
- At each prediction date, use only information that would actually have been available then. Align after-close news to the next trading session.
- Compare forecasts with a naive last-value/random-walk baseline; compare portfolios with equal weight and a benchmark.
- Include transaction costs/slippage where feasible; disclose limitations. A model losing to a baseline is a valid finding.
- Freeze choices before final testing where possible; do not tune against the test period.
- This is research/decision support, not live brokerage execution or a guarantee of returns.

## Build philosophy
Build in small tested steps. Explain what each step achieves and why. Prefer reproducibility, simple baselines, and transparent results over complexity for its own sake.

## Core concept
Historical backtesting is like replaying the past: on every simulated date, the system must know only what an investor could have known on that date. Seeing future information is look-ahead bias/data leakage.

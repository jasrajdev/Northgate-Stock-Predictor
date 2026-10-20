# Ideas Backlog

Keep all useful ideas here, including speculative or untested ones. Label status; do not silently delete or dismiss them. Add rationale, risks, and a test when known.

## First-phase price/volume baseline
- Start with daily OHLCV and adjusted-price data for a documented Indian stock universe plus a benchmark.
- Candidate derived features: returns, rolling volatility, moving averages, and volume changes. Derive them only from information available on each prediction date.
- Compare with a naive baseline before adding more complex features.
- Select stocks using a reproducible historical rule where possible; avoid survivorship bias from selecting only today's successful companies.
- Check corporate actions, missing trading sessions, duplicate dates, symbol changes, and whether adjusted historical prices are available.

## Evaluation ideas
- Compare forecast metrics and directional accuracy, not just a single score.
- Evaluate portfolio returns after transaction costs and slippage where feasible.
- Compare against naive forecast, buy-and-hold, equal-weight, and simple momentum baselines.
- Test sentiment both included and excluded to measure whether it adds value.
- If time permits, freeze a strategy and paper-track it on new data as an extension; this is not a core PRD requirement.

## Later-phase macro/news/event research
- Company-specific news: earnings, management changes, contracts, lawsuits, product launches, and other material announcements.
- Government and regulatory events: budgets, tax/import-duty changes, sector rules, public spending, and other policy announcements.
- RBI and macroeconomic events: policy-rate decisions, inflation, growth, currency, bond yields, and other releases.
- Global events: crude oil, geopolitical shocks, major overseas market moves, and global interest-rate decisions.
- Market-wide flows and activity: benchmark moves, foreign/institutional flows where reliable data is available, trading volume, and volatility.
- Potential event-study module: investigate large stock moves and retrieve time-relevant events as candidate explanations. Must distinguish plausible explanations from demonstrated causation.
- Potential news classifier: tag each item by topic/event type, relevant company/sector, sentiment, timestamp, source, and duplicate status; compare its predictive contribution with simpler features.
- Potential adaptive/source-weighting model: only consider after a reliable chronological baseline exists and after testing whether source/category reliability is stable out of sample. Do not assume a complex agentic system is needed.

## Research leads
- “Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques” (2022): https://doi.org/10.1080/08839514.2022.2111134 — inspect its data fields and, especially, split/evaluation methodology.
- “Understanding the Impact of News Articles on the Movement of Market Index: A Case on Nifty 50” (arXiv:2412.06794): https://arxiv.org/abs/2412.06794 — phase-2 broad news-topic research.
- “NIFTY Financial News Headlines Dataset” (arXiv:2405.09747): https://arxiv.org/abs/2405.09747 — phase-2 news-pipeline methodology.

## Process ideas
- Use fixed random seeds and log data date ranges, versions, parameters, and results.
- Use free Google Colab for deep learning if local hardware is a bottleneck.

## Untested
Nothing listed here should be treated as proven until tested out of sample.

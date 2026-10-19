# Ideas Backlog

Keep all useful ideas here, including speculative or untested ideas. Label status; do not silently delete or dismiss them. Add rationale, risks, and a test when known.

## Evaluation ideas
- Compare forecast metrics and directional accuracy, not just a single score.
- Evaluate portfolio returns after transaction costs and slippage where feasible.
- Compare against naive forecast, buy-and-hold, equal-weight, and simple momentum baselines.
- Test sentiment both included and excluded to measure whether it adds value.
- If time permits, freeze a strategy and paper-track it on new data as an extension; this is not a core PRD requirement.

## Process ideas
- Use fixed random seeds and log data date ranges, versions, parameters, and results.
- Use free Google Colab for deep learning if local hardware is a bottleneck.

## Candidate information groups for India-focused research
- Company-specific news: earnings, management changes, contracts, lawsuits, product launches, and other material announcements.
- Government and regulatory events: budgets, tax/import-duty changes, sector rules, public spending, and other policy announcements.
- RBI and macroeconomic events: policy-rate decisions, inflation, growth, currency, bond yields, and other releases.
- Global events: crude oil, geopolitical shocks, major overseas market moves, and global interest-rate decisions.
- Market-wide flows and activity: benchmark moves, foreign/institutional flows where reliable data is available, trading volume, and volatility.
- Price/volume-derived features: returns, rolling volatility, moving averages, and unusual-volume measures.
- Potential event-study module: investigate large stock moves and retrieve time-relevant events as candidate explanations. Must distinguish plausible explanations from demonstrated causation.
- Potential news classifier: tag each item by topic/event type, relevant company/sector, sentiment, timestamp, source, and duplicate status; compare its predictive contribution with simpler features.
- Potential adaptive/source-weighting model: only consider after a reliable chronological baseline exists and after testing whether source/category reliability is stable out of sample. Do not assume a complex agentic system is needed.

## Research leads to review
- Dasgupta et al., “Understanding the Impact of News Articles on the Movement of Market Index: A Case on Nifty 50” (arXiv:2412.06794). Directly relevant to the idea that topic categories beyond company-specific financial news may matter. Review method, dataset, limitations, and reproducibility before adopting conclusions.
- Saqur et al., “NIFTY Financial News Headlines Dataset” (arXiv:2405.09747). Useful for how headlines were filtered, deduplicated, topic-ranked, timestamped/paired with market data, and evaluated. The paper's dataset is US-equity-oriented, so methods may transfer more readily than its actual market data.
- Tetlock, “Giving Content to Investor Sentiment: The Role of Media in the Stock Market” (Journal of Finance, 2007; DOI: 10.1111/j.1540-6261.2007.01232.x). Foundational research on media pessimism, prices, and volume; not India-specific.
- Araci, “FinBERT: Financial Sentiment Analysis with Pre-trained Language Models” (arXiv:1908.10063). Background for finance-specific sentiment classification; not proof that sentiment improves Indian stock forecasts.
- Official data starting points to evaluate: NSE daily reports/bhavcopy for exchange data and RBI Database on Indian Economy (DBIE) for economic/financial time series. Check coverage, terms, historical availability, and publication timestamps before selecting.

## Untested
Nothing listed here should be treated as proven until tested out of sample.

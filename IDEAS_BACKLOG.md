# Research Backlog

This file is for a small number of useful research directions, not a transcript of every brainstorming thought. Nothing here is a confirmed implementation decision.

## Data and market coverage
- Verify reliable historical Indian equity OHLCV and corporate-action-adjusted data, benchmark series, licensing, and reproducibility.
- Investigate point-in-time index constituents to reduce survivorship bias.
- Candidate derived features include lagged returns, volatility, moving averages, and volume changes; test incremental value out of sample.

## News and event information
- Investigate whether official company announcements and relevant follow-up coverage add predictive value beyond price/volume data.
- Keep any proposed source, API, keyword strategy, event categories, model, and automation workflow unselected until feasibility and historical timestamp coverage are checked.

## Evaluation
- Compare against naive forecasts, equal-weight portfolios, and an appropriate market benchmark.
- Measure forecast quality, recommendation outcomes, and portfolio results separately.
- Include costs, turnover, drawdown, trade count, and uncertainty; do not optimise win rate alone.

## Research references
- “Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques” (2022): https://doi.org/10.1080/08839514.2022.2111134
- “Understanding the Impact of News Articles on the Movement of Market Index: A Case on Nifty 50”: https://arxiv.org/abs/2412.06794
- “NIFTY Financial News Headlines Dataset”: https://arxiv.org/abs/2405.09747

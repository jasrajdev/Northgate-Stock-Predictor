# Research Review — NIFTY 50 Prediction Paper (2022)

Source reviewed: user's research briefing uploaded 2026-11-09, based on “Stock Market Prediction of NIFTY 50 Index Applying Machine Learning Techniques” (Fathali, Kodia, Ben Said, 2022), DOI: https://doi.org/10.1080/08839514.2022.2111134

This is a working review of the supplied research notes, not an independent reproduction of the paper.

## What the briefing reports
- Task: forecast the NIFTY 50 index using historical daily data.
- Source and period: Quandl; 1 Jan 2014 to 31 Dec 2018 (five years).
- Inputs described: Date, Open, High, Low, Close, Volume, and daily trend/change information; experiments also compare combinations of OHLCV variables.
- Architectures: RNN, LSTM, CNN.
- Preprocessing described: cleaning, duplicate removal, missing-value handling, discretisation, and StandardScaler.
- Training: backpropagation; experiments with activation functions and epoch counts (including 250 and 500).
- Evaluation described: MSE, RMSE, MAE, R-squared and accuracy.
- Reported conclusion: LSTM has lower MSE than RNN and CNN in some comparisons.

## Useful lessons for Northgate
- OHLCV is a reasonable starting data contract for daily market research.
- Compare multiple architectures rather than assuming deep learning is automatically better.
- Feature combinations and hyperparameters can change reported results.
- Inspect performance across different periods; market behaviour can change.
- Learn the training pipeline (preprocessing, sequences, model fit, evaluation) from this paper.

## Important caveats recorded in the user's briefing
- The paper's task is index forecasting, not stock-by-stock selection or a portfolio backtest.
- It uses only 2014–2018, shorter than the Northgate PRD's 8–10-year target.
- The briefing reports an 80/20 train/test split and K-fold cross-validation in training, but the supplied description does not establish that folds preserve chronological order. Random K-fold would be inappropriate for time series.
- StandardScaler is described in the paper as scaling to [-1, 1]; that is not what StandardScaler does. StandardScaler produces zero mean and unit variance (subject to data distribution). Northgate must fit it on training data only.
- The briefing reports mixed metric evidence: LSTM is reported best on some RMSE/MSE comparisons, while an RNN R-squared result is higher in another comparison. Therefore "LSTM is best" is too broad; model ranking depends on metric and experiment.
- The paper's reported MSE/RMSE values must not be interpreted as percentage accuracy without checking target scaling and inverse transformation.
- The paper does not establish profitable recommendations, trading costs, slippage, portfolio allocation, or risk-adjusted portfolio superiority.
- The paper's accessible details contain ambiguity about whether the target is returns or closing prices; verify exact target construction in the original article before reproducing.

## Northgate conclusion
Use this paper as a learning reference for sequence modelling and OHLCV experimentation. Do not copy its validation design blindly, do not treat its LSTM result as a proven trading edge, and do not use it as evidence that a 70% five-day BUY win rate is achievable. Northgate's own chronological out-of-sample backtest must answer that question.

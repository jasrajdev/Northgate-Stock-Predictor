# Northgate First Experiment Recovery Report

**Written:** 2026-11-14 (IST). **Type:** documentation and verification only. Nothing was run, retrained, downloaded, modified, committed or pushed.

**Primary source:** the Kaggle notebook as downloaded by the project owner.

| Item | Value |
|---|---|
| Local path | `~/Desktop/Northgate - Stock Predictor/notebookf887dc542c.ipynb` (outside the Git repository) |
| Size / modified | 441,545 bytes / 2026-11-14 04:57 IST |
| SHA-256 | `5e2374b5b7f48496f7c5b6d2c34d95dfac2ed23df502b796957109ce3725aa7e` |
| Cells | 79 code cells, 0 markdown cells; 65 non-empty; execution counts 2–75 |
| Kernel | Python 3.13.16 |

**Secondary sources:** GitHub `origin/main` at commit `62e5272` (2026-11-14 04:35 IST; unchanged at time of writing): `STATUS.md`, `PROJECT_NOTEBOOK.md`, `DECISIONS.md`, `docs/CONTINUITY_PROTOCOL.md`, `docs/MODEL_TRAINING_GUIDE.md`.

**How to read this report.** Every figure is copied from saved notebook output unless marked otherwise. Tags: **[NB cell n]** = notebook cell index (0-based) whose saved output contains the figure; **[DOC]** = statement in repository documentation; **[DERIVED]** = my arithmetic on notebook figures; **[UNRESOLVED]** = cannot be settled from available material.

> **Recovery status in one line:** the notebook preserves the code, the logs, the summary tables and partial detail tables as *printed text*. **No result file (CSV/JSON) and no model checkpoint has been recovered.** The file names and sizes listed in sections 11 and 12 are a directory listing printed inside the notebook, not files that exist locally or on GitHub.

---

## 1. Experiment overview and purpose

The notebook is one continuous Kaggle session that (a) cloned the repository at commit `df50a7ca361d21aae721a2ceef45ec03b56fd35e` [NB 60], (b) rebuilt the price/volume dataset from Yahoo Finance [NB 15, 28], (c) ran the committed single-split training scripts, found problems, patched three scripts in place [NB 26, 27, 32, 39], re-ran them [NB 29, 34, 41], and (d) wrote and ran a new walk-forward program, `scripts/run_walk_forward.py` [NB 68, 70, 72].

Purpose of the final run [NB 70 docstring, 72]: compare four classical models and four deep sequence models against two simple baselines on next-session prediction for ten Indian equities, using five expanding chronological validation folds, **without loading the test partition**.

It is a price/volume-only experiment: no macro, CPI, news or sentiment inputs appear in the feature list [NB 67, 75].

## 2. Dataset and ticker universe

**The dataset was rebuilt inside the notebook; it is not the dataset stored on the project owner's Mac.** [NB 15, 28: `!python scripts/prepare_gpu_training_data.py`]

| Quantity | Notebook value | Source |
|---|---|---|
| Market rows | 29,506 | NB 15 |
| Labelled rows | 29,495 | NB 15, 18 |
| Feature count reported by the build | 24 | NB 15 |
| Split rows train / validation / test | 21,708 / 6,390 / 1,397 | NB 15, 52 |
| Build checks | duplicate_ticker_date 0; all_target_dates_after_feature_dates true; missing_target_values 0; all_rows_assigned_once true; test_is_latest_six_months true | NB 15 |
| Train feature-date range | 2016-01-01 → 2023-12-28 | NB 52, 67 |
| Validation feature-date range | 2023-12-29 → 2026-05-08 | NB 52, 67 |
| Test feature-date range (row count and dates only) | 2026-05-11 → 2026-11-11 | NB 52 |
| Instruments per split | 11 (10 equities + `^NSEI`) | NB 52 |
| Equity-only rows used by the walk-forward program | training 19,740; validation 5,810 | NB 69, 71 |

**Tickers (10)** [NB 67, 75]: BHARTIARTL.NS, HDFCBANK.NS, HINDUNILVR.NS, ICICIBANK.NS, INFY.NS, ITC.NS, LT.NS, RELIANCE.NS, SUNPHARMA.NS, TCS.NS. The benchmark `^NSEI` is excluded from model fitting [NB 69: "Benchmark excluded: ^NSEI"].

Notes:
* The build was executed twice (NB 15 before the ATR patch, NB 28 after). Both printed the same row counts. Each run re-downloaded from Yahoo.
* The data files themselves (`market_panel.csv`, `feature_panel.csv`, `modeling_dataset_next_day.csv`, `splits/*.csv`, `data/raw/market_panel.parquet`) existed only in the Kaggle working directory [NB 60]. **They are not recovered.**
* The mismatch between "feature_count 24" (build) and "25 features" (training) is explained by the training code adding the raw `Adj Close` column to the 24 engineered features [NB 67].

## 3. Target variable and feature list

**Training target** [NB 70 `TARGET`, 75 `"target"`]: `target_log_return_t1`, the natural log of next-session adjusted close over current adjusted close. Internal consistency check printed in the notebook: maximum absolute difference between the stored target and `log(target_adj_close_t1 / Adj Close)` on validation rows [NB 46].

**Price reconstruction for metrics** [NB 70 `calculate_metrics`]: `actual_price = Adj Close × exp(actual return)`, `predicted_price = Adj Close × exp(predicted return)`.

**Features (25)** [NB 67, 69, 71, 75], in notebook order:

`Adj Close`, `return_1d`, `return_2d`, `return_5d`, `return_10d`, `return_20d`, `price_sma_ratio_5`, `price_sma_ratio_10`, `price_sma_ratio_20`, `price_sma_ratio_50`, `price_sma_ratio_100`, `price_sma_ratio_200`, `price_ema_ratio_12`, `price_ema_ratio_26`, `volatility_5d`, `volatility_10d`, `volatility_20d`, `volatility_60d`, `rsi_14`, `macd_pct`, `macd_signal_pct`, `atr_14_pct`, `volume_sma_ratio_20`, `volume_change_1d`, `obv_change_20`.

**Excluded columns** [NB 70 `EXCLUDED`]: `Date`, `Ticker`, `Name`, `target_date_t1`, `target_adj_close_t1`, `target_log_return_t1`, `target_direction_t1`, `Open`, `High`, `Low`, `Close`, `Volume`, `Dividends`, `Stock Splits`. The program aborts unless exactly 25 features are found and none starts with `target_`.

Deep models additionally receive a 10-element one-hot ticker indicator [NB 70 `make_sequences`].

`atr_14_pct` is the notebook-patched version (true range computed from High/Low rescaled by `Adj Close / Close`, previous close = previous `Adj Close`) [NB 26], not the version in the committed script.

## 4. Training and validation methodology

All from the source of `run_walk_forward.py` as saved in NB 70, and its log in NB 72.

* **Data read:** `train.csv` and `validation.csv` only. `test.csv` is never opened by this program.
* **Fold construction:** by feature `Date`. For each fold, training = all train rows plus validation rows with `Date` before the fold start; validation = validation rows with fold start ≤ `Date` < fold end. The program asserts that training dates end before validation dates and that all 10 tickers are present.
* **Classical models:** fitted **separately per ticker** per fold on that ticker's training rows. Preprocessing sits inside each scikit-learn `Pipeline` (median imputation; standard scaling for Ridge and SVR), so it is fitted on training rows only.
* **Deep models:** **one pooled model per architecture per fold** across all 10 tickers, input = last 30 sessions of the 25 standardised features plus the ticker one-hot.
  * Scaling: medians, means and standard deviations computed on the fitting data only, values clipped to ±10.
  * Stage A (epoch selection): the last 15 % of each fold's training **dates** (`INNER_VALIDATION_FRACTION = 0.15`) form an inner stopping set; train on the earlier 85 % with early stopping (patience 6, maximum 30 epochs) on inner-set MSE of log return.
  * Stage B: a fresh model is trained on the full fold training data for the selected number of epochs.
  * Stage C: the fold's validation rows are scored once. The last 29 training sessions per ticker are supplied as context so every validation row has a 30-session window; context rows are not scored.
  * Optimiser AdamW (lr 1e-3, weight decay 1e-4), Huber loss, gradient clipping 1.0, mixed precision on CUDA, shuffled mini-batches within the training set.
* **Seed:** 42 for Python, NumPy and PyTorch; one run per model (no repeated seeds).
* **Hyper-parameters:** fixed values; no tuning or grid search was performed.
* **Test partition:** report field `"test_partition_loaded": false` [NB 75]. This value is a literal written by the program, consistent with its code, which does not read `test.csv`. **No final-test evaluation was performed.** See section 15 for one earlier cell that opened `test.csv` for row counts.

**Selected epochs (Stage A)** [NB 72 log]:

| Fold | LSTM | GRU | BiLSTM | Transformer |
|---|---|---|---|---|
| 2024-H1 | 9 | 6 | 4 | 7 |
| 2024-H2 | 7 | 14 | 8 | 11 |
| 2025-H1 | 7 | 6 | 8 | 10 |
| 2025-H2 | 6 | 12 | 5 | 4 |
| 2026-YTD | 6 | 5 | 13 | 3 |

## 5. The five validation folds

Fold windows as coded [NB 70 `FOLDS`] and equity row counts as printed by the dry run [NB 69, 71]:

| Fold | Start (inclusive) | End (exclusive) | Training rows | Validation rows | Validation dates |
|---|---|---|---|---|---|
| 2024-H1 | 2024-01-01 | 2024-07-01 | 19,750 | 1,200 | 120 |
| 2024-H2 | 2024-07-01 | 2025-01-01 | 20,950 | 1,260 | 126 |
| 2025-H1 | 2025-01-01 | 2025-07-01 | 22,210 | 1,230 | 123 |
| 2025-H2 | 2025-07-01 | 2026-01-01 | 23,440 | 1,260 | 126 |
| 2026-YTD | 2026-01-01 | 2026-06-01 | 24,700 | 850 | 85 |

* Validation rows sum to 5,800 [DERIVED]; `validation.csv` has 5,810 equity rows. The remaining 10 rows (one per ticker, feature date 2023-12-29) precede the first fold and are used as training rows, which is why fold 1 training is 19,750 rather than 19,740 [DERIVED from NB 69].
* The 2026-YTD window is coded to 2026-06-01, but validation data ends at feature date 2026-05-08 [NB 67].
* An earlier fold audit that included `^NSEI` printed 21,719 / 23,039 / 24,425 / 25,778 / 27,164 training rows and 1,320 / 1,386 / 1,353 / 1,386 / 934 validation rows [NB 54, 67]; those are 11-instrument counts and were not the rows used for training.
* Per-ticker rows in fold 1: `train_rows` 1,975, `validation_rows` 120 for BHARTIARTL.NS [NB 75].

## 6. Models and baselines

**Baselines** [NB 70 `train_classical_fold`]:

| Name | Price forecast | Direction forecast |
|---|---|---|
| `Naive_Last_Adjusted_Close` | predicted log return = 0, i.e. next adjusted close = current adjusted close | sign of 0 |
| `Always_Up_Direction_Baseline` | identical zero-return price forecast | always +1 |

**Classical (per ticker)** [NB 70 `make_classical_models`]:

| Name | Configuration |
|---|---|
| `Ridge` | median imputer → StandardScaler → Ridge(alpha=10.0) |
| `RandomForest` | median imputer → RandomForestRegressor(n_estimators=120, min_samples_leaf=3, max_features=0.8, random_state=42) |
| `SVR_RBF` | median imputer → StandardScaler → SVR(C=1.0, epsilon=0.01, kernel="rbf") |
| `XGBoost` | median imputer → XGBRegressor(n_estimators=250, max_depth=4, learning_rate=0.04, subsample=0.85, colsample_bytree=0.85, objective="reg:squarederror", tree_method="hist", device="cuda", random_state=42) |

No `XGBoost_CPU_Fallback` rows appear in the result counts [NB 74]. XGBoost emitted a device-mismatch warning (model on `cuda:0`, input on CPU) and continued [NB 72].

**Deep (pooled)** [NB 70 classes `Recurrent`, `TransformerRegressor`]:

| Name | Architecture |
|---|---|
| `LSTM` | 1-layer LSTM (hidden 24) → Dropout 0.15 → Linear 16 → ReLU → Linear 1 |
| `GRU` | same with a GRU cell |
| `BiLSTM` | same with a bidirectional LSTM (width 48) |
| `Transformer` | Linear projection to 24 + learned positional parameter → 1 encoder layer (4 heads, feed-forward 48, dropout 0.1, GELU) → LayerNorm → Linear 16 → GELU → Linear 1; last time step used |

**Result-set integrity** [NB 74]: 500 rows; 50 per model for each of the 10 names; 100 per fold; 10 unique tickers; 5 unique folds. `fold_results.csv` columns: `fold, ticker, model, train_rows, validation_rows, mae, rmse, mape_pct, r2, directional_accuracy, selected_epochs` [NB 75].

## 7. Overall performance metrics

**Metric definitions as coded** [NB 70 `calculate_metrics`, `save_summary`]:

* `mae`, `rmse`: mean absolute error and root mean squared error **in adjusted-close price units (rupees)** between `actual_price` and `predicted_price`.
* `mape_pct`: mean of |actual − predicted| / |actual| × 100, in price space.
* `r2`: scikit-learn `r2_score` on prices.
* `directional_accuracy`: mean of `sign(actual return) == sign(direction forecast)`. This is a sign-equality test with three possible signs (−1, 0, +1). It is a separate quantity from price MAE.
* **Overall summary = the unweighted mean of the 50 per-(ticker, fold) values of each metric** for a model (`groupby("model").mean()`). It is not an error pooled over rows, and it is not weighted by rows or normalised by price level.

**`model_summary.csv` as printed** [NB 73], sorted by `mae`:

| model | mae | rmse | mape_pct | r2 | directional_accuracy |
|---|---|---|---|---|---|
| Always_Up_Direction_Baseline | 18.325321 | 25.358721 | 0.997656 | 0.904756 | 0.493920 |
| Naive_Last_Adjusted_Close | 18.325321 | 25.358721 | 0.997656 | 0.904756 | 0.004947 |
| GRU | 18.454483 | 25.472045 | 1.005211 | 0.904125 | 0.500852 |
| BiLSTM | 18.485269 | 25.450290 | 1.005394 | 0.903726 | 0.501671 |
| Transformer | 18.531481 | 25.587486 | 1.011868 | 0.903019 | 0.501856 |
| Ridge | 18.642707 | 25.715983 | 1.015369 | 0.901134 | 0.503348 |
| LSTM | 19.019540 | 25.954508 | 1.040146 | 0.898246 | 0.497155 |
| RandomForest | 19.992273 | 26.938232 | 1.078312 | 0.892663 | 0.487741 |
| XGBoost | 20.251257 | 27.260608 | 1.097621 | 0.889107 | 0.496889 |
| SVR_RBF | 26.768896 | 34.761823 | 1.440935 | 0.831044 | 0.495020 |

**Reading the naive comparison.**

* **Price error.** Both baselines make the same price forecast, so they share `mae` 18.325321. **Every trained model has a higher overall MAE than the naive forecast.** The closest is GRU at 18.454483, which is 0.70 % worse [DERIVED: (18.454483 − 18.325321) / 18.325321]. No trained model beats the baseline overall on MAE, RMSE, MAPE or R².
* **Direction.** The interpretable comparator is `Always_Up_Direction_Baseline` at 0.493920. Trained models range from 0.487741 (RandomForest) to 0.503348 (Ridge). The largest margin over always-up is 0.94 percentage points (Ridge) [DERIVED]. No uncertainty estimate exists for any of these numbers.
* **Why the naive baseline shows 0.004947 directional accuracy.** Its forecast return is exactly 0, so `sign(0) = 0`, which equals `sign(actual)` only when the actual return is exactly zero. The notebook measured 26 exact-zero returns among 5,810 validation rows, 0.4475 % [NB 46]. The figure is therefore the frequency of unchanged prices, not a measure of directional skill and not the frequency of down days.

## 8. Per-stock performance and model consistency

Computed in NB 76 from `fold_results.csv`: for each ticker and model, row-weighted averages across the five folds; `mae_improvement_pct = (naive_mae − mae) / naive_mae × 100` (positive = better than naive); `directional_improvement_pp` relative to always-up.

**Model consistency across tickers** (complete, as printed) [NB 76]:

| model | stocks_beating_naive (of 10) | avg_mae_improvement_pct | avg_directional_improvement_pp | total_fold_wins (of 50) | total_direction_fold_wins (of 50) |
|---|---|---|---|---|---|
| GRU | 1 | −0.790 | 0.741 | 21 | 16 |
| BiLSTM | 3 | −0.812 | 0.293 | 15 | 12 |
| Transformer | 1 | −1.143 | 0.862 | 16 | 8 |
| Ridge | 0 | −1.894 | 0.724 | 9 | 29 |
| LSTM | 0 | −4.611 | 0.207 | 8 | 12 |
| RandomForest | 0 | −8.931 | −0.810 | 3 | 21 |
| XGBoost | 0 | −10.385 | 0.138 | 1 | 28 |
| SVR_RBF | 0 | −43.480 | −0.172 | 0 | 21 |

No model beats the naive MAE on more than 3 of 10 stocks, and no model wins more than 21 of its 50 ticker-fold comparisons on MAE.

**Per-ticker table: only 10 of 80 rows are preserved.** The notebook displayed the 80-row table truncated to its first and last five rows (in both the text and HTML outputs). The preserved rows [NB 76]:

| ticker | model | mae | naive_mae | mae_improvement_pct | mape_pct | directional_accuracy | always_up_da | directional_improvement_pp | folds_beating_naive_mae | folds_beating_up_direction |
|---|---|---|---|---|---|---|---|---|---|---|
| BHARTIARTL.NS | BiLSTM | 16.171 | 16.218 | 0.292 | 0.993 | 0.534 | 0.529 | 0.517 | 3 | 1 |
| BHARTIARTL.NS | GRU | 16.416 | 16.218 | −1.123 | 1.007 | 0.495 | 0.529 | −3.448 | 1 | 0 |
| BHARTIARTL.NS | Transformer | 16.450 | 16.218 | −1.303 | 1.007 | 0.522 | 0.529 | −0.690 | 2 | 0 |
| BHARTIARTL.NS | LSTM | 16.523 | 16.218 | −1.834 | 1.013 | 0.541 | 0.529 | 1.207 | 2 | 2 |
| BHARTIARTL.NS | Ridge | 16.711 | 16.218 | −2.902 | 1.022 | 0.517 | 0.529 | −1.207 | 2 | 2 |
| TCS.NS | Ridge | 33.551 | 32.916 | −1.887 | 1.007 | 0.469 | 0.453 | 1.552 | 0 | 3 |
| TCS.NS | LSTM | 35.023 | 32.916 | −6.930 | 1.058 | 0.460 | 0.453 | 0.690 | 0 | 1 |
| TCS.NS | RandomForest | 37.183 | 32.916 | −13.332 | 1.119 | 0.474 | 0.453 | 2.069 | 0 | 2 |
| TCS.NS | XGBoost | 38.214 | 32.916 | −16.394 | 1.152 | 0.488 | 0.453 | 3.448 | 0 | 3 |
| TCS.NS | SVR_RBF | 48.567 | 32.916 | −48.931 | 1.487 | 0.488 | 0.453 | 3.448 | 0 | 3 |

**Not preserved:** all rows for HDFCBANK, HINDUNILVR, ICICIBANK, INFY, ITC, LT, RELIANCE, SUNPHARMA; BHARTIARTL rows for RandomForest, SVR_RBF, XGBoost; TCS rows for BiLSTM, GRU, Transformer. The identity of the stocks counted in `stocks_beating_naive` (other than BHARTIARTL for BiLSTM) cannot be read from the notebook. Naive MAE differs by price level (16.218 for BHARTIARTL, 32.916 for TCS), which is why rupee MAE averages weight high-priced stocks more.

**Raw per-(fold, ticker) rows preserved:** the first five rows of `fold_results.csv`, all 2024-H1 / BHARTIARTL.NS [NB 75]:

| model | train_rows | validation_rows | mae | rmse | mape_pct | r2 | directional_accuracy |
|---|---|---|---|---|---|---|---|
| Naive_Last_Adjusted_Close | 1975 | 120 | 13.832189 | 19.724927 | 1.137386 | 0.970373 | 0.000000 |
| Always_Up_Direction_Baseline | 1975 | 120 | 13.832189 | 19.724927 | 1.137386 | 0.970373 | 0.583333 |
| Ridge | 1975 | 120 | 13.700001 | 19.442260 | 1.126255 | 0.971216 | 0.550000 |
| RandomForest | 1975 | 120 | 14.409122 | 19.772446 | 1.185902 | 0.970230 | 0.491667 |
| SVR_RBF | 1975 | 120 | 19.296254 | 24.465387 | 1.594098 | 0.954422 | 0.416667 |

The 400-row fold-level detail table is preserved for 10 rows only (five 2024-H1 BHARTIARTL rows and five 2026-YTD TCS rows) [NB 76]: 2024-H1 BHARTIARTL `mae_improvement_pct` / `directional_improvement`: BiLSTM 0.4787 / 0.0000; GRU 1.0144 / 0.0000; LSTM 2.4707 / 0.0500; RandomForest −4.1709 / −0.0917; Ridge 0.9557 / −0.0333. 2026-YTD TCS: RandomForest −12.0994 / 0.0000; Ridge −3.4408 / 0.0000; SVR_RBF −68.9734 / 0.0000; Transformer −3.0017 / 0.0000; XGBoost −18.2057 / −0.0235.

## 9. Fold-level performance

**`fold_model_summary.csv`, all 50 rows as printed** [NB 73]. Each value is the unweighted mean over the 10 tickers in that fold.

| fold | model | mae | rmse | mape_pct | r2 | directional_accuracy |
|---|---|---|---|---|---|---|
| 2024-H1 | Always_Up_Direction_Baseline | 18.575915 | 26.631592 | 1.058668 | 0.885162 | 0.516667 |
| 2024-H1 | BiLSTM | 18.892400 | 26.877822 | 1.080445 | 0.882521 | 0.516667 |
| 2024-H1 | GRU | 18.622834 | 26.652516 | 1.061580 | 0.884822 | 0.516667 |
| 2024-H1 | LSTM | 18.868467 | 26.848737 | 1.072457 | 0.882017 | 0.510833 |
| 2024-H1 | Naive_Last_Adjusted_Close | 18.575915 | 26.631592 | 1.058668 | 0.885162 | 0.001667 |
| 2024-H1 | RandomForest | 19.364885 | 27.519592 | 1.110664 | 0.875667 | 0.480000 |
| 2024-H1 | Ridge | 18.788367 | 26.782638 | 1.072409 | 0.883336 | 0.498333 |
| 2024-H1 | SVR_RBF | 26.064057 | 34.886624 | 1.488375 | 0.801673 | 0.495833 |
| 2024-H1 | Transformer | 18.958618 | 26.964655 | 1.084288 | 0.881819 | 0.516667 |
| 2024-H1 | XGBoost | 19.473339 | 27.554197 | 1.122388 | 0.874754 | 0.494167 |
| 2024-H2 | Always_Up_Direction_Baseline | 17.853815 | 24.666022 | 0.927807 | 0.919223 | 0.519048 |
| 2024-H2 | BiLSTM | 17.888614 | 24.703990 | 0.930342 | 0.918884 | 0.480159 |
| 2024-H2 | GRU | 18.159693 | 24.899958 | 0.942907 | 0.918029 | 0.519048 |
| 2024-H2 | LSTM | 18.774353 | 25.378632 | 0.980264 | 0.914608 | 0.518254 |
| 2024-H2 | Naive_Last_Adjusted_Close | 17.853815 | 24.666022 | 0.927807 | 0.919223 | 0.000794 |
| 2024-H2 | RandomForest | 20.164908 | 26.713629 | 1.043799 | 0.901906 | 0.496032 |
| 2024-H2 | Ridge | 18.244580 | 24.976238 | 0.942486 | 0.917852 | 0.517460 |
| 2024-H2 | SVR_RBF | 26.778708 | 34.446597 | 1.412171 | 0.838534 | 0.496825 |
| 2024-H2 | Transformer | 17.853813 | 24.671666 | 0.927346 | 0.919264 | 0.519048 |
| 2024-H2 | XGBoost | 21.104263 | 27.578607 | 1.113792 | 0.887062 | 0.507143 |
| 2025-H1 | Always_Up_Direction_Baseline | 18.395176 | 25.433411 | 1.008421 | 0.924747 | 0.500813 |
| 2025-H1 | BiLSTM | 18.676706 | 25.695518 | 1.020660 | 0.922956 | 0.500813 |
| 2025-H1 | GRU | 18.633798 | 25.651937 | 1.023715 | 0.923521 | 0.491057 |
| 2025-H1 | LSTM | 18.745127 | 25.713016 | 1.028496 | 0.922160 | 0.502439 |
| 2025-H1 | Naive_Last_Adjusted_Close | 18.395176 | 25.433411 | 1.008421 | 0.924747 | 0.008130 |
| 2025-H1 | RandomForest | 19.507458 | 26.184781 | 1.064002 | 0.920271 | 0.489431 |
| 2025-H1 | Ridge | 18.612329 | 25.743409 | 1.026930 | 0.920575 | 0.490244 |
| 2025-H1 | SVR_RBF | 28.452940 | 35.996532 | 1.520116 | 0.859264 | 0.495935 |
| 2025-H1 | Transformer | 18.419462 | 25.439734 | 1.008962 | 0.924582 | 0.500813 |
| 2025-H1 | XGBoost | 19.850108 | 26.675073 | 1.083120 | 0.918873 | 0.500813 |
| 2025-H2 | Always_Up_Direction_Baseline | 14.145668 | 19.203442 | 0.749305 | 0.892340 | 0.477778 |
| 2025-H2 | BiLSTM | 14.165110 | 19.201940 | 0.750361 | 0.892020 | 0.477778 |
| 2025-H2 | GRU | 14.131286 | 19.213630 | 0.748557 | 0.892441 | 0.519841 |
| 2025-H2 | LSTM | 15.274013 | 20.058303 | 0.812679 | 0.877251 | 0.477778 |
| 2025-H2 | Naive_Last_Adjusted_Close | 14.145668 | 19.203442 | 0.749305 | 0.892340 | 0.002381 |
| 2025-H2 | RandomForest | 16.919407 | 21.931698 | 0.851720 | 0.873504 | 0.492063 |
| 2025-H2 | Ridge | 14.491113 | 19.793552 | 0.768327 | 0.886914 | 0.509524 |
| 2025-H2 | SVR_RBF | 19.016383 | 25.149289 | 0.999467 | 0.825937 | 0.486508 |
| 2025-H2 | Transformer | 14.205378 | 19.379876 | 0.753243 | 0.891122 | 0.517460 |
| 2025-H2 | XGBoost | 15.543216 | 20.636597 | 0.810425 | 0.877620 | 0.497619 |
| 2026-YTD | Always_Up_Direction_Baseline | 22.656030 | 30.859136 | 1.244077 | 0.902309 | 0.455294 |
| 2026-YTD | BiLSTM | 22.803515 | 30.772181 | 1.245163 | 0.902247 | 0.532941 |
| 2026-YTD | GRU | 22.724801 | 30.942185 | 1.249297 | 0.901811 | 0.457647 |
| 2026-YTD | LSTM | 23.435740 | 31.773852 | 1.306836 | 0.895194 | 0.476471 |
| 2026-YTD | Naive_Last_Adjusted_Close | 22.656030 | 30.859136 | 1.244077 | 0.902309 | 0.011765 |
| 2026-YTD | RandomForest | 24.004710 | 32.341457 | 1.321376 | 0.891966 | 0.481176 |
| 2026-YTD | Ridge | 23.077146 | 31.284077 | 1.266694 | 0.896991 | 0.501176 |
| 2026-YTD | SVR_RBF | 33.532392 | 43.330074 | 1.784547 | 0.829812 | 0.500000 |
| 2026-YTD | Transformer | 23.220134 | 31.481498 | 1.285502 | 0.898309 | 0.455294 |
| 2026-YTD | XGBoost | 25.285357 | 33.858567 | 1.358377 | 0.887223 | 0.484706 |

**Fold-level consistency summary** (from `fold_model_summary.csv`) [NB 77]:

| model | folds_beating_naive (of 5) | average_mae_improvement_pct | best_fold_improvement_pct | worst_fold_improvement_pct | folds_beating_direction (of 5) | average_directional_improvement_pp |
|---|---|---|---|---|---|---|
| GRU | 1 | −0.693 | 0.102 | −1.713 | 2 | 0.693 |
| BiLSTM | 0 | −0.844 | −0.137 | −1.704 | 1 | 0.775 |
| Transformer | 1 | −1.021 | 0.000 | −2.490 | 1 | 0.794 |
| Ridge | 0 | −1.763 | −1.144 | −2.442 | 2 | 0.943 |
| LSTM | 0 | −4.010 | −1.575 | −7.977 | 2 | 0.324 |
| RandomForest | 0 | −9.760 | −4.247 | −19.608 | 2 | −0.618 |
| XGBoost | 0 | −10.486 | −4.831 | −18.206 | 2 | 0.297 |
| SVR_RBF | 0 | −45.483 | −34.433 | −54.676 | 2 | 0.110 |

The only fold-level MAE "wins" are GRU in 2025-H2 (14.131286 vs 14.145668, +0.102 %) and Transformer in 2024-H2 (17.853813 vs 17.853815, +0.000 %; see section 15). The best directional margin is BiLSTM in 2026-YTD: 0.532941 vs always-up 0.455294 (+7.765 pp) on 850 rows, in a fold where its MAE is worse than naive. Period-by-period improvement figures for all 40 model-fold pairs are in NB 77 and agree with the table above.

## 10. Training environment and execution duration

| Item | Value | Source |
|---|---|---|
| Platform | Kaggle notebook, working directory `/kaggle/working/Northgate-Stock-Predictor` | NB 69 |
| Python | 3.13 (`/usr/local/lib/python3.13/dist-packages`; kernel metadata 3.13.16) | NB 72, metadata |
| Device | `cuda`; GPU `Tesla T4`; VRAM 14.56 GiB | NB 72, 75 |
| Sequence / batch / hidden | 30 / 8 / 24 | NB 72, 75 |
| Max epochs / patience | 30 / 6 | NB 75 |
| Mixed precision | True | NB 72 |
| `inner_stopping_fraction` | 0.15 | NB 75 |
| **Walk-forward duration** | `elapsed_seconds` 4986.31 (≈ 83.1 minutes [DERIVED]) | NB 75 |
| `completed_result_rows` | 500 | NB 75 |
| Repository commit cloned | `df50a7ca361d21aae721a2ceef45ec03b56fd35e`, with three modified scripts | NB 60 |

Earlier single-split runs in the same session: classical script 22.99 s [NB 16], 19.58 s [NB 29], 36.49 s [NB 41]; deep script duration not printed [NB 34].

[UNRESOLVED] The notebook file's metadata records `"accelerator": "none"`, `"isGpuEnabled": false`, `"isInternetEnabled": false`, while the saved logs show a Tesla T4 and successful `git clone`, `pip install` and Yahoo downloads. The logs are evidence of what ran; the metadata probably reflects the notebook's settings when it was saved or downloaded. Not verifiable from the file alone.

## 11. Generated report files (listing only, not recovered)

Directory listing printed by the notebook for `reports/walk_forward/` [NB 78]:

| # | File name | Recorded size (bytes) | Content known from the notebook |
|---|---|---|---|
| 1 | `reports/walk_forward/dry_run_audit.json` | 2,166 | Fields defined in NB 70 `dry_run`; values match NB 71 printout |
| 2 | `reports/walk_forward/fold_model_summary.csv` | 5,743 | **All 50 rows** printed (section 9) |
| 3 | `reports/walk_forward/fold_results.csv` | 66,986 | Shape (500, 11); **only 5 rows** printed |
| 4 | `reports/walk_forward/model_summary.csv` | 1,100 | **All 10 rows** printed (section 7) |
| 5 | `reports/walk_forward/walk_forward_report.json` | 1,262 | **Full JSON** printed |

## 12. Model checkpoint files (listing only, not recovered)

Directory listing printed for `models/walk_forward/` [NB 78]. Each file was saved with `state_dict`, model name, fold, sequence length, hidden size, selected epochs, tickers, features and the scaling medians/means/standard deviations [NB 70].

| # | File name | Recorded size (bytes) |
|---|---|---|
| 1 | `models/walk_forward/2024-H1_bilstm_best.pt` | 55,389 |
| 2 | `models/walk_forward/2024-H1_gru_best.pt` | 24,124 |
| 3 | `models/walk_forward/2024-H1_lstm_best.pt` | 30,023 |
| 4 | `models/walk_forward/2024-H1_transformer_best.pt` | 37,807 |
| 5 | `models/walk_forward/2024-H2_bilstm_best.pt` | 55,389 |
| 6 | `models/walk_forward/2024-H2_gru_best.pt` | 24,124 |
| 7 | `models/walk_forward/2024-H2_lstm_best.pt` | 30,023 |
| 8 | `models/walk_forward/2024-H2_transformer_best.pt` | 37,807 |
| 9 | `models/walk_forward/2025-H1_bilstm_best.pt` | 55,389 |
| 10 | `models/walk_forward/2025-H1_gru_best.pt` | 24,124 |
| 11 | `models/walk_forward/2025-H1_lstm_best.pt` | 30,023 |
| 12 | `models/walk_forward/2025-H1_transformer_best.pt` | 37,807 |
| 13 | `models/walk_forward/2025-H2_bilstm_best.pt` | 55,389 |
| 14 | `models/walk_forward/2025-H2_gru_best.pt` | 24,124 |
| 15 | `models/walk_forward/2025-H2_lstm_best.pt` | 30,023 |
| 16 | `models/walk_forward/2025-H2_transformer_best.pt` | 37,807 |
| 17 | `models/walk_forward/2026-YTD_bilstm_best.pt` | 55,400 |
| 18 | `models/walk_forward/2026-YTD_gru_best.pt` | 24,135 |
| 19 | `models/walk_forward/2026-YTD_lstm_best.pt` | 30,034 |
| 20 | `models/walk_forward/2026-YTD_transformer_best.pt` | 37,834 |

Total recorded checkpoint size: 736,775 bytes [DERIVED]. Classical models were not saved by the program (no persistence code in NB 70).

## 13. What the notebook actually preserves

As text inside the `.ipynb` file:

1. **Complete source of `run_walk_forward.py`** (final version, NB 70; an earlier dry-run-only version, NB 68).
2. **The four in-place patches** to committed scripts (NB 26 ATR; NB 27 raw-column exclusion in the classical script; NB 32 raw-column exclusion, score mask and training context in the deep script; NB 39 log-return target, metric function and baselines in the classical script), plus `git diff` output for the three modified scripts (NB 61, 63) and full printed copies of the patched `train_deep_models.py` and `train_baseline_models.py` (NB 64, 65).
3. **Full training log** of the walk-forward run, including per-epoch inner validation losses and selected epochs (NB 72).
4. **Complete tables:** `model_summary.csv` (10 rows), `fold_model_summary.csv` (50 rows), `walk_forward_report.json`, model-consistency tables (NB 76, 77), period table (40 rows, NB 77).
5. **Partial tables:** 5 of 500 rows of `fold_results.csv`; 10 of 80 per-ticker rows; 10 of 400 fold-level detail rows.
6. **Dataset build summary** and split sizes (NB 15, 52), dataset column list and descriptive statistics (NB 18, 19), adjustment-ratio table (NB 23).
7. **Earlier single-split results** (section 15): classical summaries (NB 16, 29, 41, 42), deep-model report JSON (NB 35), per-stock tables (NB 17, 36).
8. **Exploratory analyses on validation rows:** simple momentum direction rules (always up 49.66 %, previous-day momentum 48.11 %, 5-day 49.52 %, 20-day 49.41 %, on 5,810 rows; actual direction 50.34 % down / 49.66 % up) [NB 44], return distribution and zero-return analysis [NB 45, 46], feature-target correlations and regime splits [NB 47–51].
9. **Directory listings** with names and sizes of the 5 report files and 20 checkpoints (NB 78).

## 14. Artifacts currently unavailable

Checked locations: the local repository working tree, GitHub `origin/main`, the folder containing the notebook, and a file-name search of the Mac. None of the following was found.

| Artifact | Status |
|---|---|
| `fold_results.csv` (495 of 500 rows unseen) | **Not recovered.** Existed at `/kaggle/working/.../reports/walk_forward/` |
| `model_summary.csv`, `fold_model_summary.csv`, `walk_forward_report.json` | **Files not recovered**; contents fully readable in the notebook |
| `dry_run_audit.json` | **Not recovered**; contents inferable from NB 70/71 only |
| 20 walk-forward checkpoints (`*.pt`) | **Not recovered.** Model weights cannot be reconstructed from the notebook |
| 4 single-split checkpoints `models/deep/*_best.pt` | Not recovered |
| `reports/validation/*` (single-split CSV/JSON) and the backup folder `/kaggle/working/northgate_experiment_01/` (8 files, NB 43) | Not recovered |
| Kaggle dataset: `market_panel.csv` (29,506 rows), `feature_panel.csv`, `modeling_dataset_next_day.csv`, `splits/*.csv`, `data/raw/market_panel.parquet`, `gpu_data_build_report.json` | Not recovered. A later rebuild would not be identical because Yahoo restates history |
| `scripts/run_walk_forward.py` and the patched scripts as files | Not in Git; recoverable as text from the notebook |
| Per-prediction outputs (row-level forecasts) | Never written by the program |
| Loss-curve data as files | Never written; per-epoch values exist only in the NB 72 log |

Whether the Kaggle session's working directory still exists is unknown to me.

## 15. Research conclusions and limitations

**Conclusions supported by the notebook**

1. On the unweighted mean of per-ticker-fold price MAE, **no trained model beat the naive last-adjusted-close forecast overall**. The best three (GRU, BiLSTM, Transformer) were 0.7 %–1.1 % worse; Ridge 1.7 % worse; LSTM 3.8 % worse; RandomForest 9.1 %, XGBoost 10.5 % and SVR_RBF 46.1 % worse [DERIVED from section 7].
2. Directional accuracy for every trained model lies between 48.8 % and 50.3 % overall, against 49.4 % for always-up. No reliable directional edge is shown.
3. No model is consistent across folds or stocks (sections 8, 9).
4. The test partition was not evaluated.

**Limitations and items preserved for investigation (not corrected here)**

* **L1. Different dataset from the Mac.** 29,506 / 29,495 rows and splits 21,708 / 6,390 / 1,397, versus 29,484 / 29,473 and 21,708 / 6,379 / 1,386 documented for the Mac files. The Kaggle validation set therefore extends one session further (11 more rows across 11 instruments).
* **L2. Executed code is not the committed code.** Three scripts were patched in the session and the walk-forward program was created there.
* **L3. "Overall" MAE is a mean of 50 rupee-denominated MAEs**, so higher-priced stocks carry more weight. The overall `r2` (≈ 0.90) is likewise a mean of per-ticker-fold R² values on price levels and is high for the naive forecast too; it is not evidence of skill.
* **L4. Naive directional accuracy 0.004947** is a convention artefact (section 7). Fold values 0.001667, 0.000794, 0.008130, 0.002381, 0.011765.
* **L5. Suspicious: Transformer in 2024-H2.** MAE 17.853813 vs naive 17.853815 (difference 0.000002 [DERIVED]) and MAPE 0.927346 vs 0.927807, with directional accuracy exactly equal to always-up (0.519048). In 2024-H1, 2025-H1 and 2026-YTD its directional accuracy also equals always-up exactly. This pattern is what a model emitting a near-constant, slightly positive return would produce. It is counted as a fold "win" in NB 77 (`folds_beating_naive` = 1, `best_fold_improvement_pct` = 0.000). Not verifiable without the predictions or checkpoint.
* **L6. Suspicious: identical directional accuracy across models.** BiLSTM, GRU and Transformer all show 0.516667 in 2024-H1; BiLSTM and LSTM show 0.477778 (= always-up) in 2025-H2; XGBoost and BiLSTM show 0.500813 (= always-up) in 2025-H1. Several deep models may be predicting one sign for nearly all rows in some folds. Unverified.
* **L7. Exact-zero returns.** 26 validation rows have exactly zero return, several on the same dates across tickers (e.g. target dates 2025-03-18 and 2026-01-15 in the NB 46 sample). The separate dataset audit in this folder found the same dates to be stale or phantom vendor bars in the Mac data. Their effect on these results is unquantified.
* **L8. Model scope differs.** Classical models are per ticker; deep models are pooled across tickers.
* **L9. No tuning, one seed, no confidence intervals.** Differences of a few tenths of a percent cannot be interpreted.
* **L10. `Adj Close` level is an input feature**, standardised across all tickers together for the deep models.
* **L11. `test.csv` was opened once in the session** [NB 52] to print row count (1,397), date range and tickers. No test-period outcome or metric was computed. Whole-dataset descriptive statistics (`describe()` over all 29,495 rows, including target columns) and per-ticker adjustment ratios were also displayed [NB 18, 23]. This is disclosed for completeness; it is not a test evaluation.
* **L12. Validation history was reused.** The same 2024–2026 validation rows were examined in the earlier single-split runs and exploratory cells before the walk-forward run.
* **L13. Earlier single-split results in the same notebook are not comparable with the walk-forward table and must not be mixed with it:**

  | Run | Result as printed |
  |---|---|
  | Committed classical script, price-level target, 32 features [NB 16] | Naive MAE 17.996946, R² 0.977125, DA 0.004475; Ridge MAE 38.335093; RandomForest 222.905313 (R² −2.186898); XGBoost 233.565655 (R² −2.308429); SVR_RBF 819.181702 (R² −23.932263) |
  | After excluding raw columns, 25 features, still price-level target [NB 29] | Naive 17.996949; Ridge 18.778804; XGBoost 268.269982; RandomForest 285.216821; SVR_RBF 889.490993 |
  | After switching the classical target to log return [NB 41, 42] | Always-up / naive MAE 17.996949 (DA 0.496558 / 0.004475); Ridge 18.476517 (DA 0.500172); RandomForest 19.555503 (0.497246); XGBoost 19.879592 (0.500000); SVR_RBF 28.530803 (0.490189) |
  | Patched deep script, single split, batch 8, hidden 24 [NB 34, 35] | LSTM MAE 18.100739, DA 0.494836; GRU 18.000908, 0.496558; **BiLSTM 17.988352**, 0.501549; Transformer 18.028345, 0.500688; R² ≈ 0.9991 for all; 19,450 training and 5,810 validation sequences |

  In that single-split run BiLSTM's MAE (17.988352) is below the classical script's naive figure (17.996949). This is **not** a valid win: the deep script computed metrics pooled over all rows while the classical script averaged per-ticker metrics (hence R² 0.9991 vs 0.9771), and the deep script chose its stopping epoch on the same validation rows it reported. Preserved here as an inconsistency, not a finding.

## 16. Recommended next actions

1. **Recover the physical artifacts if the Kaggle session or its saved version still exists:** `reports/walk_forward/` (5 files), `models/walk_forward/` (20 files), `reports/validation/`, `models/deep/`, `/kaggle/working/northgate_experiment_01/`, and the `data/processed` files. Record SHA-256 for each. If they are gone, record that explicitly in `STATUS.md`.
2. **Place the notebook under version control** (or at least record its SHA-256 above) so the only surviving record is not a single file on the Desktop.
3. **Extract the code that already exists as text** (`run_walk_forward.py` and the three patched scripts) into the repository under an experiment folder, unchanged, labelled as Experiment 01. This needs the owner's approval; it was not done here.
4. **Correct the documentation discrepancies** listed below by appended, dated notes.
5. **If `fold_results.csv` is recovered:** verify the per-ticker tables, complete the 70 missing per-ticker rows, and check items L5 and L6.
6. **Do not rerun or extend the experiment** until the price-basis, bad-row and split-freeze issues in `FULL_TECHNICAL_AUDIT.md` are decided. Label this run "Experiment 01: exploratory".

---

## Discrepancies between the notebook and repository documentation

| # | Documentation statement | Notebook evidence | Assessment |
|---|---|---|---|
| 1 | `STATUS.md` (2026-11-14) and `PROJECT_NOTEBOOK.md`: the run used "the existing train/validation data" / "existing training and validation CSVs" | Dataset rebuilt in-session: 29,506 market rows; validation 6,390; test 1,397 [NB 15, 52] | **Inaccurate.** A different, later download with a different feature set from the Mac files |
| 2 | `PROJECT_NOTEBOOK.md`: naive 0.495 % directional score arises because "a zero forecast is classified as non-positive/down … mostly reflects the frequency of down days" | Code compares `sign(actual)` with `sign(0)`; matches only on exact-zero returns; 26 of 5,810 = 0.4475 % [NB 46, 70] | **Inaccurate explanation**; the number itself is correctly reported |
| 3 | Both documents call the headline figure "pooled price MAE" | Unweighted mean of 50 per-(ticker, fold) MAEs [NB 70 `save_summary`] | Imprecise wording |
| 4 | `docs/MODEL_TRAINING_GUIDE.md`: defaults batch 16, hidden 32; classical MAE "computed on adjusted-close levels"; outputs under `reports/validation/` and `models/deep/` | Run used batch 8, hidden 24; all models trained on log return; outputs under `reports/walk_forward/` and `models/walk_forward/` [NB 72, 75, 78] | Guide describes the committed scripts, not the executed experiment |
| 5 | `docs/MODEL_TRAINING_GUIDE.md` and `STATUS.md`: "24 backward-looking features" | 25 model inputs: 24 engineered + `Adj Close` [NB 67] | Minor; clarify |
| 6 | Documents state the final test partition "was not loaded" | True for the walk-forward program and both training scripts; `test.csv` was read once for shape and dates [NB 52] | Accurate for training/evaluation; incomplete as a description of the session |
| 7 | `STATUS.md`: "Generated Kaggle outputs/checkpoints were verified in the user's session" | Notebook contains a listing with sizes [NB 78] | Consistent; note that existence was verified on Kaggle only, and nothing is held locally |
| 8 | Repository scripts at `origin/main` | Scripts were modified in-session; `run_walk_forward.py` does not exist in the repository [NB 60, 61] | Repository cannot reproduce the documented results |
| 9 | `STATUS.md`: "Audit verified 500 total result rows: 50 per model and 100 per fold; 10 unique tickers; 5 unique folds"; overall MAE and directional figures; BiLSTM 53.29 % in 2026-YTD; GRU small advantage in 2025-H2 | Match NB 73, 74, 77 | **Consistent** |
| 10 | `DECISIONS.md` (2026-11-12): first target is next-session adjusted close; (2026-11-13) test cut-off computed from the latest target date | Models were trained on log return, prices reconstructed; cut-off moved with the later download | Not contradictory, but the executed target and the moved boundary are not recorded as decisions |

## Verification record for this report

Performed after writing, by script against the notebook file: all 448 decimal figures in sections 7, 8, 9 and 15 occur in the saved outputs (the one exception, 0.000002, is a derived difference); all 60 rows of the overall and fold tables match NB 73 as whole rows; all 20 checkpoint names and sizes and all 5 report names and sizes match NB 78; the 20 selected-epoch values match the NB 72 log. One error was found and corrected during verification (the checkpoint size total). The text contains no statement that any artifact is held locally or that the test partition was evaluated.

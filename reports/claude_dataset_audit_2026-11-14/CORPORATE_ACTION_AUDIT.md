# Corporate-Action and Price-Basis Audit

Audit run: 2026-11-14 (IST), read-only. Companion files: `corporate_action_event_ledger.csv` (17 rows), `price_basis_comparison.csv` (110 rows), `evidence/02_price_basis_output.txt`, `evidence/03_event_windows_output.txt`.

Evidence labels used throughout: **[OFFICIAL]** = read from an NSE file whose SHA-256 was checked in this audit; **[VENDOR]** = Yahoo value; **[DERIVED]** = arithmetic on those two; **[NEWS]** = web-search result, not an exchange notice; **[REPO]** = a claim made in the project documents, not re-fetched.

## 1. Verdict in one paragraph

The "price-basis problem" is now largely **explained, not mysterious**. Yahoo's `Open/High/Low/Close` (even with `auto_adjust=False`) are **back-adjusted for every later split, bonus, rights issue and most demergers**, by one multiplicative factor per event applied to every earlier day. `Adj Close` additionally back-adjusts for every later cash dividend. On 110 symbol-dates checked against official NSE files, Yahoo's Close ÷ NSE Close equals the product of the factors of later events **exactly (maximum residual 0.0 at 6 decimals)**, OHLC all scale by the same factor, and volume scales by the inverse factor, on all 110 rows. Two events are **not** handled consistently by Yahoo and corrupt the labels: the ITC demerger (partly adjusted, by a smaller amount than the special pre-open session implies) and the HINDUNILVR demerger (not adjusted at all). The earlier project statements that BHARTIARTL's gap was "unexplained" and that RELIANCE's "multiplier is unknown" are resolved by the tables below.

## 2. Validation of the 11 downloaded NSE files (the "user-reported" status is now closed)

All 11 files exist locally. Every SHA-256 equals the value recorded in `docs/DATA_RESEARCH.md` / `STATUS.md`. [OFFICIAL]

| Group | Files | Schema parsed | Date inside file | Target EQ row |
|---|---|---|---|---|
| Legacy CM bhavcopy (ZIP, `testzip()` clean) | 22-Apr-2019, 23-Apr-2019, 12/13/14-May-2020 | `SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN` + empty trailing column | `TIMESTAMP` equals file name in all 5 | exactly 1 per target symbol |
| Full bhavcopy (CSV, not HTML) | RELIANCE 25/28/29-Oct-2024; HDFCBANK 25/26/28-Aug-2025 | `SYMBOL, SERIES, DATE1, PREV_CLOSE, OPEN_PRICE, … DELIV_PER` (leading spaces in every header and value; `-` for missing delivery) | `DATE1` equals file name in all 6 | exactly 1 per target symbol |

Practical notes for any future parser: the two layouts differ; the full-bhavcopy layout has **no ISIN**; headers need stripping; all ten project symbols have an `EQ` row in every file (10 of 10 on 11 dates = 110 comparisons).

## 3. What Yahoo does, event by event (110 official comparisons)

`factor` = Yahoo Close ÷ NSE Close on the stated date. [DERIVED]

**Symbols with no price-adjusting action after the date compared are identical to NSE.** 82 of 110 symbol-dates have ratio 1.00000 (SUNPHARMA, TCS, INFY, LT, ICICIBANK on all 11 dates; HINDUNILVR on all 11 dates; BHARTIARTL from 2024; ITC from 2025-08; RELIANCE from 2024-10-28; HDFCBANK from 2025-08-26).

| Symbol | Dates compared | Observed factor | Explained by (events after that date) | Residual |
|---|---|---|---|---|
| BHARTIARTL | 22-Apr-2019 | 0.90126 | 0.91818 (2019 rights) × 0.98157 (2021 rights) | 0 |
| BHARTIARTL | 23-Apr-2019 … 14-May-2020 | 0.98157 | 2021 rights only | 0 |
| RELIANCE | 22/23-Apr-2019, 12-May-2020 | 0.45717 | 0.99062 (2020 rights) × 0.92300 (2023 demerger) × 0.5 (2024 bonus) | 0 |
| RELIANCE | 13/14-May-2020 | 0.46150 | 0.92300 × 0.5 | 0 |
| RELIANCE | 25-Oct-2024 | 0.50000 | 2024 bonus | 0 |
| HDFCBANK | Apr 2019 | 0.25000 | 0.5 (2019 face-value split) × 0.5 (2025 bonus) | 0 |
| HDFCBANK | May 2020 – Oct 2024, 25-Aug-2025 | 0.50000 | 2025 bonus | 0 |
| ITC | Apr 2019 – 29-Oct-2024 | 0.96292 | 2025 demerger (partial) | 0 |
| HINDUNILVR | all 11 | 1.00000 | **no adjustment although the 2025-12-05 demerger is later** | 0 |

Consequences:

1. **BHARTIARTL 23-Apr-2019 (Yahoo ₹310.667 vs NSE ₹316.50):** fully explained. The two rights issues give 0.98157 → 316.50 × 0.98157 = 310.67. The *1.34 % Yahoo return vs −9.42 % raw return* is the rights-issue price drop: Yahoo's back-adjustment with the 19:67 rights at ₹220 uses a factor 0.91818, within 0.01 % of the NSE derivative formula's 0.91826 computed on the raw cum-date close (₹349.40). That the cash-equity vendor factor equals the F&O formula is an **observation here**, not a rule; it must not be assumed for other events.
2. **RELIANCE 13-May-2020 (Yahoo ₹690.611 vs NSE ₹1,496.45):** fully explained as 0.4615 = 0.5 (2024 bonus) × 0.923 (2023 demerger). The earlier warning "do not double Yahoo" stands: doubling gives 1,381 ≠ 1,496. The 2020 rights factor (0.99062) matches the F&O formula (0.99061).
3. **The RELIANCE 2023 factor 0.92300** is derived from the vendor only. Its basis (the value of the demerged Jio Financial shares) is not reproduced here: ledger CA-11 is "partly explained".
4. **Volume** behaves consistently (Yahoo volume = NSE volume ÷ factor on all 110 rows): the series is on a *current-share-count basis*, i.e. a restated history.

## 4. Event windows and the damage to labels

`label` = `target_log_return_t1` on the session before the ex-date (the label that crosses the event). Local labels are computed from `Adj Close`.

| Event | Yahoo ex-date return | NSE raw ex-date return | Label crossing event | Partition | Assessment |
|---|---|---|---|---|---|
| BHARTIARTL rights 2019-04-23 | −1.34 % | −9.42 % | −0.01353 | train | Vendor strips the rights drop; economically defensible for a price-return series |
| RELIANCE rights 2020-05-13 | +2.12 % | +1.16 % | +0.02100 | train | Same |
| BHARTIARTL rights 2021-09-27 | −0.44 % | not held | −0.00445 | train | Same; partly-paid structure not modelled |
| RELIANCE demerger 2023-07-20 | −0.12 % | not held | −0.00121 | train | Adjusted; basis unverified |
| RELIANCE bonus 2024-10-28 | +0.49 % | −49.76 % | +0.00488 | validation | Correct (split-normalised) |
| **ITC demerger 2025-01-06** | **−4.55 %** | ≈ −8.09 % [NEWS] | **−0.04654** | **validation** | **Partly adjusted.** Vendor removed ₹17.9 (factor 0.96292 × ₹481.60 [NEWS prior close]); the special pre-open session implied about ₹26 (₹481.6 → ₹455.6 [NEWS]). Using the session value the same label would be ln(442.65/455.60) = −2.88 %: the label **overstates the loss by about 1.8 percentage points** |
| HDFCBANK bonus 2025-08-26 | −0.88 % | −50.44 % | −0.00885 | validation | Correct |
| **HINDUNILVR demerger 2025-12-05** | **−5.02 %** | not held (vendor unadjusted so equals raw) | **−0.05150** | **validation** | **Not adjusted.** The label contains the whole value of the distributed Kwality Wall's share. News figures imply about ₹40 per share [NEWS, inferred ≈ ₹29.8 listing ÷ 0.74]; that is roughly 1.6 percentage points of the −5.15 % |

Both artefact labels sit in the **validation** partition and in the 2025-H1 and 2025-H2 walk-forward folds, so the Experiment-01 numbers contain two return outliers of about −4.7 % and −5.2 % that are partly accounting artefacts. They are two rows out of 5,800 and cannot explain why models failed to beat the naive baseline, but they will matter for tail metrics, drawdowns and any BUY/SELL hit-rate analysis.

Additional events found in Yahoo's own action fields and **not previously listed in the project** (all in the training partition): ITC bonus 2016-07-01 (1.5), ICICIBANK bonus 2017-06-20 (1.1), LT bonus 2017-07-13 (1.5), RELIANCE bonus 2017-09-07 (2.0), TCS bonus 2018-05-31 (2.0), INFY bonus 2018-09-04 (2.0), HDFCBANK face-value split 2019-09-19 (2.0). Their ex-date returns look normal (−0.9 % to +2.8 %), consistent with correct split normalisation, but terms and dates are not confirmed against primary sources. **The ledger's completeness is not established**; buybacks, mergers (e.g. HDFC Ltd into HDFC Bank, 2023) and any event Yahoo does not record would need an NSE corporate-actions export per symbol.

## 5. Dividends

`Adj Close ÷ Close` steps on **exactly the 183 dates with a Yahoo `Dividends` entry and nowhere else** (0 unexplained steps in any ticker; the product of future dividend factors reproduces the ITC ratio to 3×10⁻⁷). Dividend amounts were **not** checked against exchange records. Consequence: `Adj Close` is a retrospective total-return-style series; its absolute level on a date changes whenever a later dividend is paid.

## 6. The five price concepts: where the project's data sits

| Concept | Available now? | Notes |
|---|---|---|
| 1. Contemporaneous unadjusted exchange price | Only 11 dates × 10 symbols (110 rows) [OFFICIAL] | Bhavcopy for every date would need ~2,680 daily files or per-symbol security-wise exports |
| 2. Retrospectively corporate-action-adjusted price | Yes: Yahoo `Close` (splits, bonuses, rights, ITC/RELIANCE demergers; **not** HUL) | Levels change with every new action |
| 3. Dividend-adjusted price | Yes: Yahoo `Adj Close` | Also restated by each new dividend |
| 4. Total-return / shareholder-wealth series | **No** | Needs dividends + rights entitlements + partly-paid calls + demerged-share values; the project has none of the last three |
| 5. Point-in-time price series for a historical simulation | **No** | Would require adjusting only by events with announcement date ≤ t |

## 7. Are features and labels affected by retrospective restatement?

* **Returns, ratios, RSI, volatility:** invariant to a factor that is constant across the lookback window. Where a lookback window *spans* an ex-date, a dividend factor changes slightly inside the window; the effect is at most the dividend yield (≈ 1–2 %) on the day and is a small, known distortion, not a leak of future prices.
* **Rupee-level inputs** (`Adj Close` as a model input, `sma_*`, `ema_*`, `macd`, `volume_sma_20`): the value at date *t* depends on all dividends and (for `Close`) all splits/rights/demergers up to the download date, i.e. on information after *t*. A model fed these can learn the restatement pattern. **Remove them** (task T-013).
* **`adj_close_vs_close`:** equals (1 − product of future dividend factors) − 1. This is a **direct look-ahead feature** in the Mac `feature_panel.csv`. ITC example: −32.0 % on 2016-01-04, reconstructed from future dividends to 3×10⁻⁷. It also behaves like a time index. It is **not** in the 25 features used by Experiment 01 (the Kaggle build uses a different script) but it is in the local dataset and would enter the committed `train_baseline_models.py` and `train_deep_models.py` if run on it.
* **Label `target_adj_close_t1`:** a level on the restated basis; not comparable across download dates. The log-return label is safe except at the two artefact events above.

## 8. Target-definition options and consequences (decision memo)

| Option | Definition | Pros | Cons / consequences |
|---|---|---|---|
| **A. Keep PRD-literal** | `target_adj_close_t1` (Yahoo Adj Close level) | Matches PRD wording and `DECISIONS.md` | Level restated by every future dividend; pooled MAE is dominated by high-priced stocks (LT + TCS = 41 % of the naive baseline's pooled absolute error); two demerger artefacts |
| **B. Log-return label on vendor Adj Close (what Experiment 01 effectively trained)** | `target_log_return_t1`, price reported as `P_t·exp(r̂)` | Scale-free; PRD allows "next-day log return" in §3.4; only two artefacts | Not the PRD's "forward closing price" unless converted; still vendor-derived |
| **C. B plus event-window handling** | Same as B but rows whose label window contains an unresolved event (CA-13, CA-15, optionally CA-11) are flagged and excluded or corrected in a sensitivity arm | Removes the known artefacts without inventing factors | Slightly fewer rows; requires a written rule fixed before the next run |
| **D. Official-price rebuild** | Rebuild OHLCV from NSE files, adjust with a ledger-based, documented factor series | Most defensible; separates concepts 1–5 | 1.5–3 days plus a data-rights decision (D-14) |
| **E. Shareholder-wealth return** | Include rights/demerger entitlements | Economically complete | Needs partly-paid call schedules and demerged-share prices; weeks of work; not required by the PRD |

**Recommendation:** adopt **C now** (primary: next-session log return on the existing vendor series with the two artefacts flagged and a sensitivity arm); keep PRD-literal price as a derived report quantity `P_t·exp(r̂)`; start **D** only for validation of the full history (T-012) and schedule E as an optional extension. **Approval needed from the project owner: D-02 (basis/target) and D-03 (event-window policy).** Nothing in the data or labels has been modified by this audit.

## 9. Open items (nothing silently assumed)

1. Primary-source confirmation of dates and ratios for CA-01…CA-06 and CA-08.
2. Official bhavcopy for 18/19-Sep-2019, 24/27-Sep-2021, 19/20-Jul-2023, 3/6-Jan-2025, 4/5-Dec-2025 (T-011).
3. Exchange notices (special pre-open session discovered prices) for ITC and HUL; the figures above are from news pages.
4. Why Yahoo's RELIANCE-2023 factor is 0.923 and whether it equals the value implied by the special session.
5. Per-symbol NSE corporate-actions export to establish ledger completeness (T-010).
6. Dividend amounts against exchange records.

## 10. Sources

* NSE circular FAOP/65846 (ITC demerger): https://nsearchives.nseindia.com/content/circulars/FAOP65846.pdf
* NSE circular FAOP/64621 (RELIANCE bonus): https://nsearchives.nseindia.com/content/circulars/FAOP64621.pdf
* NSE Clearing circular CMPT/57559 (RELIANCE demerger): https://archives.nseindia.com/content/circulars/CMPT57559.pdf
* NSE circular FAOP/49720 (BHARTIARTL 2021 rights): https://archives.nseindia.com/content/circulars/FAOP49720.pdf
* Airtel 2021 Letter of Offer (BofA-hosted copy): https://business.bofa.com/content/dam/flagship/in/en/investment-banking/Bharti-Airtel-Limited-Letter-of-Offer--2021.pdf
* Airtel 2019 Letter of Offer: https://assets.airtel.in/teams/simplycms/web/docs/Letter_of_Offer_dated_April_19_2019.pdf
* HUL scheme information memorandum: https://nsearchives.nseindia.com/corporates/offerdocument/scheme/IM_KWIL.pdf
* ITC special pre-open session (news): https://www.business-standard.com/amp/markets/capital-market-news/itc-shares-slip-on-hotel-demerger-record-date-125010600849_1.html and https://upstox.com/news/market-news/stocks/itc-hotels-demerger-itc-to-conduct-special-pre-open-session-today-a-quick-summary-of-everything-you-need-to-know/article-138946 (accessed 2026-11-14; secondary)
* HUL demerger (news): https://www.business-standard.com/amp/markets/capital-market-news/hindustan-unilever-drops-as-kwality-wall-s-demerger-takes-effect-125120500744_1.html and https://upstox.com/news/market-news/stocks/kwality-wall-s-lists-at-26-discount-on-nse-after-demerger-from-hul-all-you-need-to-know/article-189456/ (accessed 2026-11-14; secondary)
* Yahoo adjusted-close definition: https://in.help.yahoo.com/kb/adjusted-close-sln28256.html [REPO]
* NSE All Reports (bhavcopy formats, unadjusted-price note): https://www.nseindia.com/all-reports [REPO]

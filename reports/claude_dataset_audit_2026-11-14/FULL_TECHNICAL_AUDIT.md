# Northgate Stock Predictor: Full Technical Audit

**Audit timestamp:** started 2026-11-14 05:04 IST (UTC+05:30), completed the same day. **Auditor:** Claude (AI assistant), run locally in the repository. **Mode:** read-only. Nothing outside `reports/claude_dataset_audit_2026-11-14/` was created or changed (one `git fetch` updated remote-tracking refs only; the working tree and branch were not touched).

This file is the technical source of truth. Companion deliverables in the same folder: `REMAINING_TASKS.csv/json`, `DATASET_INVENTORY.csv/json`, `DATA_SOURCE_MATRIX.csv`, `CORPORATE_ACTION_AUDIT.md`, `corporate_action_event_ledger.csv`, `price_basis_comparison.csv`, `FEATURE_LABEL_DICTIONARY.csv`, `LEAKAGE_CODE_AUDIT.md`, `IMPLEMENTATION_ROADMAP.md`, `USER_DECISIONS_REQUIRED.md`, `NORTHGATE_DATASET_AUDIT.pdf`. Reproducible audit code is in `audit_scripts/` (10 scripts); raw outputs in `evidence/`.

## 0. How to read the evidence labels

| Label | Meaning |
|---|---|
| **VERIFIED** | Recomputed or inspected from actual files in this audit |
| **REPO** | Stated in project documents with a source URL; not re-fetched here |
| **USER-REPORTED** | Terminal/Kaggle output recorded in documents; origin files not available to me |
| **WEB** | Checked by web search/fetch on 2026-11-14 (source listed in §Q) |
| **INFERENCE** | My reasoning from the above |
| **DECISION** | Only the project owner can settle it |

## 1. What was inspected

* **Documents (GitHub `origin/main` @ 62e5272, 2026-11-14 04:35 IST):** `README.md`, `STATUS.md` (610 lines, full), `PROJECT_NOTEBOOK.md` (full), `DECISIONS.md`, `QUESTIONS.md`, `IDEAS_BACKLOG.md`, `LEARNING_LOG.md`, `docs/CONTINUITY_PROTOCOL.md`, `docs/PRD_REQUIREMENTS.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/MODEL_TRAINING_GUIDE.md`, `docs/GPU_LAPTOP_SETUP.md`, `docs/RESEARCH_PAPER_REVIEW.md`, `data/external/README_CPI.md`, `config/northgate_universe.json`, `reports/data_quality/cpi_market_panel_merge_2026-11-13.md` (all full). `docs/DATA_RESEARCH.md` (1,835 lines): lines 1–80 and 942–1,835 read in full; lines 81–941 (the CPI research log) read by section headings and through the `STATUS.md` summaries of the same work. `docs/RESEARCH_ROADMAP.md` lines 1–166 full, remainder by headings. `docs/DATASET_INVENTORY.md` lines 1–50 full, remainder by headings (it duplicates `STATUS.md`/`DATA_RESEARCH.md`). `SUBMISSION_PLAN.md` lines 1–40 and headings. **These partial reads are a limitation of this audit.**
* **Original PRD v1.0:** found at `~/Downloads/f773513d5994f93126d19f185d32a851.docx` (43,724 bytes); text extracted and read in full (913 lines).
* **Code:** all 13 scripts and 2 tests on `origin/main`, the 4 local scripts (identical to GitHub), the untracked `download_nse_bhavcopy.py`, and the Kaggle notebook (79 cells, including the 1,170-line `run_walk_forward.py` it writes).
* **Data:** every file under `data/`, `reports/`, the 18 CPI workbooks and other files in `~/Desktop/Northgate - Stock Predictor/`, `~/Downloads/cpi_33.xlsx` (hashed only), CPI CSVs on GitHub.
* A second clone exists at `~/Projects/Northgate-Stock-Predictor` (last commit 2026-10-19, initial structure only); not used.

## 2. Classification of the project's existing claims

| Claim in project documents | Status after audit |
|---|---|
| Market panel 29,484 rows, 11 instruments, 2016-01-01 → 2026-11-09 | **VERIFIED** (10 equities × 2,681 + index 2,674) |
| 24 engineered features | **VERIFIED** for the Mac pipeline; a *different* 24 for the GPU pipeline |
| 29,473 labelled rows; 11 rows dropped; 0 duplicate keys; 0 missing targets; targets after features; no non-positive targets | **VERIFIED** (recomputed bit-identically) |
| Splits 21,708 / 6,379 / 1,386; boundaries 2023-12-29 / 2026-05-08 / 2026-05-11 | **VERIFIED** (files equal recomputed partitions) |
| Processed panel preserves raw Yahoo values | **VERIFIED for all 29,484 rows**, not just the two inspected |
| Five legacy bhavcopy hashes and rows | **VERIFIED** |
| Six full-bhavcopy downloads "not yet validated" | **VERIFIED now** (hash, schema, date, EQ row) |
| BHARTIARTL 2019 Yahoo/NSE gap "unexplained" | **RESOLVED**: 2021 rights factor 0.98157 |
| Experiment used "the existing training and validation CSVs" | **INCORRECT**: Kaggle rebuilt a different dataset (29,506 / 29,495; splits 21,708 / 6,390 / 1,397) with a different feature set |
| Final test partition not loaded | **PARTLY**: not loaded by any training code; `test.csv` was opened in notebook cell 52 for row counts/dates; whole-dataset `describe()` in cell 18 |
| Preprocessing fit on training only | **VERIFIED** by code reading |
| 500 result rows; no model beat naive pooled MAE | **USER-REPORTED** (consistent with notebook printouts; result files not held) |
| Naive directional 0.495 % = "frequency of down days" | **INCORRECT explanation**: it is the share of exactly-zero returns |
| CPI: 18 workbooks, 3,990 vintage rows, 14 snapshots, 26 provisional markers, 0 duplicate keys | **VERIFIED** (rebuilt from the workbooks) |
| CPI merge: 6,115 matched / 23,369 unmatched / 22 columns / max age 300 days | **VERIFIED** (reproduced to scratch) |
| CPI tests "not yet run" | **RUN now**: pass |
| IN-FINews 3,348 articles Feb–Aug 2025 | **UNVERIFIED** (no local copy) |
| `cpi_33.xlsx` 31,460 rows | **UNVERIFIED** here (file present, hashed, not opened) |
| Macro/VIX/RBI/news data | **Confirmed absent** |

---

## A. Repository and data inventory

Full machine-readable inventory: `DATASET_INVENTORY.csv` (77 entries with size, SHA-256, rows, columns, date range, tickers, source, rights, Git status).

**A-1 (P0) Local clone is 319 commits behind GitHub.** Local `main` = 39bbc63 (2026-11-13 00:17); `origin/main` = 62e5272 (2026-11-14 04:35). 35 files differ; 24 exist only on GitHub (`config/`, `data/external/` ×8, 9 scripts, `tests/test_cpi_asof.py`, 5 docs, `requirements-dl.txt`, one report). The four pipeline scripts used to build the local data are byte-identical in both. GitHub is newer and authoritative for documents and code; the local folder is authoritative for data (which is not on GitHub). Neither was altered.

**A-2 Generated data missing from GitHub (by design):** all of `data/raw/yahoo` (11 files), `data/raw/nse_bhavcopy` (11), `data/processed` (6), `reports/data_quality/*.json` (4). They are **untracked but not ignored** (`.gitignore` has no `data/` rule): a `git add .` would publish them. (Task T-017.)

**A-3 Git-tracked data missing locally:** the 8 CPI files in `data/external/` (consequence of A-1).

**A-4 Important files outside any repository:** the Kaggle notebook (only copy of the experiment code and printed results), the 18 MoSPI workbooks (source of record for the CPI CSVs), the PRD `.docx`, `cpi_33.xlsx`, three research PDFs.

**A-5 Expected but absent everywhere:** Kaggle result CSVs and 24 checkpoints; `scripts/run_walk_forward.py`; `data/processed/market_panel_with_cpi.csv` (documented path `/mnt/data/` is a chat sandbox); outputs of `download_macro_context.py` and `download_market_context.py` (never run); any news/sentiment/RBI/VIX/TRI/flow/fundamental file; `notebooks/` and `models/` are empty.

**A-6 Duplicate / conflicting files:** two CPI availability maps identical except 4 note cells and one URL (`…CPI_PR_14Jun25.pdf` vs `…PR June 2025.pdf`); CPI snapshot CSV duplicates the two "part" files (same 3,990 keys and values); two pipelines write the same output names (§J).

**A-7 Overwritten or lost source data:** none found. Raw Yahoo files are dated 2026-11-12 01:22 and equal the panel. Risk: `download_market_data.py` and `prepare_gpu_training_data.py` overwrite in place (L-12, L-06).

**A-8 Secrets:** none found in tracked files or the working tree (no `.env`, no key patterns).

## B. Market-data quality

Source: `audit_scripts/01_market_quality.py`, `03_event_windows.py`; table `evidence/per_ticker_quality.csv`.

| Ticker | First | Last | Rows | Missing vs union calendar | Dup | Invalid OHLC | Zero-vol rows | NaN | \|log ret\| > 10 % days | Dividends | Splits | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BHARTIARTL.NS | 2016-01-01 | 2026-11-09 | 2,681 | 0 | 0 | 0 | 2 | 0 | 3 | 11 | 0 | Usable; 2 bad rows; 2 rights back-adjusted |
| HDFCBANK.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 3 | 12 | 2 | Usable; 2 bad rows; ISIN change 2019 |
| HINDUNILVR.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 2 | 22 | 0 | 2 bad rows; **demerger unadjusted (2025-12-05)** |
| ICICIBANK.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 8 | 10 | 1 | Usable; 2 bad rows |
| INFY.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 4 | 23 | 1 | Usable; 2 bad rows |
| ITC.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 1 | 0 | 5 | 17 | 1 | 1 bad row; **demerger partly adjusted (2025-01-06)** |
| LT.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 3 | 14 | 1 | Usable; 2 bad rows |
| RELIANCE.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 7 | 11 | 2 | 2 bad rows; 3 back-adjustment factors; one +11.6 % day in the sealed window (2026-11-02, High = Close = 1,300.0) **not investigated, verify officially before unsealing** |
| SUNPHARMA.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 3 | 18 | 0 | Usable; 2 bad rows |
| TCS.NS | 〃 | 〃 | 2,681 | 0 | 0 | 0 | 2 | 0 | 0 | 45 | 1 | Usable; 2 bad rows |
| ^NSEI | 2016-01-04 | 〃 | 2,674 | 6 | 0 | 0 | 28 | 0 | 1 | 0 | 0 | Price index only; 6 real sessions missing; volume unusable |

All series: 10.86 years (PRD ≥ 8 met); 0 duplicate keys; 0 NaN; 0 negative volume; 0 High/Low violations; largest calendar gap 5 days; dates are naive calendar dates (timezone stripped at `download_market_data.py:72`), which is acceptable for daily NSE data; panel sorted. Source and price basis for every equity: Yahoo via yfinance 1.8.0, back-adjusted (§C).

**Findings**

* **B-1 (P0) Phantom session 2026-01-15.** All 10 equities have Open = High = Low = Close = previous close and Volume = 0; the index has no row. NSE and BSE were closed that day for Maharashtra municipal elections [WEB]. Effects: 10 non-existent rows; 10 false zero-return labels on 2026-01-14; distorted rolling features; the "556 vs 555 matched CPI rows" discrepancy noted in project documents is this row.
* **B-2 (P0) Stale bars 2025-03-18.** 9 of 10 equities (all but ITC) are flat with zero volume, yet it was a normal session (NIFTY 22,834.30, +1.45 % [WEB]; the index row is normal). Effects: 9 false zero labels on 2025-03-17; the 2025-03-18 labels are two-day returns.
* **B-3** Those 19 rows are **all** the zero-volume equity rows, and 19 of the 26 zero-return labels in validation equities (0.448 % of 5,800). `build_features.py:62-70` treats zero volume as "unavailable volume" but keeps the stale price.
* **B-4 (P0) Missing real sessions.** Absent for every instrument: 2016-10-30 (Muhurat, Sunday) [INFERENCE from general knowledge, not re-verified], 2020-02-01 (Budget Saturday) [same], 2023-11-12 (Muhurat) [same], 2024-01-20, 2024-03-02, 2024-05-18 (special live sessions) [WEB], 2026-02-01 (Budget Sunday) [WEB: announced; not confirmed post-event], and 2026-11-08 (Muhurat listed in NSE's 2026 calendar [REPO]). Present: 2019-10-27 and 2020-11-14 (equities only), 2025-02-01 (all). Index lacks six dates the equities have (2016-01-01, 2016-08-12, 2018-01-01, 2019-01-01, 2019-10-27, 2020-11-14) plus the phantom date. PRD §3.4 requires a single exchange calendar and 0 % unresolved gaps.
* **B-5 Large moves** (38 equity days over ±10 %) cluster in March–April 2020 and known news days (e.g. ITC 2020-02-03, 2026-01-01; LT 2024-06-04); none coincides with a corporate-action date; none was removed. They were not individually verified.
* **B-6 Freshness.** Last row 2026-11-09 (retrieved 2026-11-11 19:53 UTC). 2026-11-10 was a listed holiday per repo notes; the Kaggle rebuild reached 2026-11-11/12.
* **B-7 Ticker renames, delistings, suspensions:** none observed in the ten series (continuous rows). ISIN transition: HDFCBANK INE040A01026 (2019–2020 files) → INE040A01034 not directly observed (new-format files carry no ISIN) [INFERENCE]. A symbol/ISIN master is missing.
* **B-8 Benchmark as equity:** `^NSEI` is in every partition (2,673 labelled rows) but excluded from model fitting by all training code; volume features disabled for it. Correct.
* **B-9** The pipeline's own QA (`download_report.json`) reports zero problems for every ticker; it cannot detect B-1…B-4 (L-13).

Nothing was deleted or altered. Proposed handling: decisions D-05, D-06; tasks T-007, T-008, T-009, T-117.

## C. Price basis and corporate actions

Full treatment in `CORPORATE_ACTION_AUDIT.md`. Summary:

* **C-1** Yahoo OHLC = NSE EQ price × product of factors of all *later* splits, bonuses, rights issues and (for ITC, RELIANCE) demergers; volume inversely. 110/110 official comparisons explained with zero residual; 82/110 are exactly equal to NSE.
* **C-2** Observed factors: BHARTIARTL rights 2019 0.91818, 2021 0.98157; RELIANCE rights 2020 0.99062, demerger 2023 0.92300, bonus 2024 0.5; HDFCBANK split 2019 0.5, bonus 2025 0.5; ITC demerger 2025 0.96292; **HINDUNILVR demerger 2025: none**.
* **C-3** Two validation labels are artefacts: ITC 2025-01-03 (−4.65 %, overstated by ≈ 1.8 pp) and HINDUNILVR 2025-12-04 (−5.15 %, overstated by the demerged value, order 1.5–2 pp, unmeasured).
* **C-4** Seven further split/bonus events exist in Yahoo's action fields and were not in the project's list; ledger completeness is unproven.
* **C-5** `Adj Close` steps on exactly the 183 dividend dates; it is a retrospective series; levels are not point-in-time.
* **C-6** A point-in-time adjusted series and a shareholder-wealth series do not exist; methodology and options are in the decision memo (§8 there).

Tasks T-006, T-010, T-011, T-012; decisions D-02, D-03, D-14.

## D. Macro and economic data

**Existing assets.** CPI (2012 base): release vintages (108 rows), cumulative snapshots (3,990 rows over 14 releases), availability map (18 releases), release-event table (18 rows), four scripts, three tests. Nothing else: `download_macro_context.py` has never been run; no RBI, FX or yield file exists.

**CPI verification (all VERIFIED unless noted):**

* Rebuild from the 18 workbooks with `build_cpi_vintages.py` reproduces 3,990 rows, 14 snapshots, 156 reference months, 26 provisional markers, 0 duplicate keys; values, release dates and sessions equal the committed files.
* Event table equals the Annex-I provisional headline for 18/18 releases and the same-release snapshot for 14/14.
* `next_nse_session` equals the first session after the release date in the local panel for 18/18 (including Friday releases mapped to Monday).
* 2012 vs 2024 base: all committed rows are base 2012; the merge script rejects other bases (`:55`). No splicing occurs. The 2024-base series (MoSPI releases from February 2026) is not integrated.
* Revisions preserved in the vintage files: first vs latest published combined index differs for 2025-01 (193.5 → 193.4), 2025-07 (196.0 → 196.1), 2025-09 (197.2 → 197.0). **The 18-row event table carries only the provisional figure and never the final revision** (design gap, D-1 below).
* As-of merge reproduced: 29,484 rows, 22 columns, 6,115 matched, first matched date 2024-08-13, boundary dates correct, one vintage per date, order preserved.
* The merged file was not saved in the project and was **not used in Experiment 01** (its 25 features contain no CPI column).

**Findings**

* **D-1 (P1)** CPI coverage is unusable for modelling as it stands: **0 rows of the training partition** have CPI; 20.7 % of the panel; 1,870 rows carry a value older than 45 days; the last value (Dec 2025) is carried to November 2026 (300 days). Missing: every release before July 2024 (≈ 102 for 2016-01 → 2024-06) and the 2024-base releases from February 2026.
* **D-2 (P0)** Three fused records make the two committed part files unreadable with a standard parser (L-17).
* **D-3** Release-time regime: 17:30 IST (Jul–Sep 2024 releases) then 16:00 IST; both after the 15:30 close, so the next-session rule is right. Do not invent times for older releases; when only a date is known use the next session.
* **D-4** Extending history: MoSPI's press-release archive (PDF, January 2011 onward [REPO]) gives, per month, the provisional current value, the final previous value and the release date. That supports a headline event table with revisions back to 2015. Cumulative back-history tables do not exist before the November 2024 release [REPO], so full vintage matrices cannot be rebuilt earlier, and are not needed for a headline feature. Use YoY inflation (and its change) rather than index level so the 2012→2024 base change does not require splicing.

**Source matrix:** `DATA_SOURCE_MATRIX.csv` rows S18–S26 (CPI, RBI policy rate, US yields, US CPI/unemployment via ALFRED, India yields, USD/INR, PLFS) with provider, coverage, timing, revision policy, access, cost, licence, point-in-time status and session alignment.

**Implementation plan (tasks T-103…T-107):** (1) one generic `as_of_join(panel, events, available_from)` with a staleness column; (2) RBI repo-rate event table with announcement dates; (3) USD/INR daily; (4) US daily series lagged one NSE session; (5) CPI event extension; (6) every series enters as a separate ablation block. Ranked by value/feasibility: India VIX (§E) > USD/INR > repo-rate events > US 10Y/3M and VIX > CPI YoY > US CPI/unemployment > PLFS (history too short: monthly series starts April 2025).

## E. Market context and benchmark

Nothing acquired. `download_market_context.py` (Yahoo `^INDIAVIX` + nine sector indices) has never been run.

* **Benchmark.** `^NSEI` is a price index. Portfolios built from `Adj Close` earn dividends, so comparing them with a price index flatters the portfolio by roughly the index dividend yield each year [INFERENCE; the yield figure must be measured from TRI ÷ price]. NIFTY 50 TRI exists from 30-Jun-1999 with CSV export [REPO]. Recommendation: TRI for the portfolio benchmark, `^NSEI` for beta and the market-return feature (D-08, T-101).
* **India VIX:** official date-range CSV exists [REPO]; implied 30-day volatility; close of *t* is usable for a *t+1* forecast. Rank 1 (T-102).
* **FII/FPI/DII:** aggregate, provisional, later revised; first-published vintages are not recoverable historically; lag one session and flag provisional. Rank 3; optional.
* **Sector indices:** one index per stock for relative strength; rank 4. **Breadth:** only from an official advance/decline series; computing it from today's constituents would be survivorship-biased; rank 5.

Sources S12–S17.

## F. Company fundamentals and disclosures

**Scope finding (VERIFIED against the PRD text):** the PRD requires OHLCV, indices, macro series and timestamped news. It does **not** require fundamentals, quarterly results, shareholding or annual reports. They are optional extensions.

Availability [REPO]: NSE company pages list financial results, annual reports, shareholding patterns, announcements and corporate actions, with broadcast timestamps and original/revised markers; no free bulk API with a published contract; manual per-company export; automated collection conflicts with NSE terms. BSE offers equivalent filings. Alignment rule if ever used: join by broadcast timestamp, results after 15:30 IST → next session, keep revisions as new rows, never backfill restated figures.

Recommendation: do not build a fundamentals dataset. The one cheap, useful derivative is an **earnings-announcement date flag** per ticker (40-odd dates each), which also explains many of the >10 % days in §B-5. Source S27; no task created (optional).

## G. Historical news

Nothing acquired; IN-FINews is not on disk. Source comparison (S28–S33):

| Source | History | Timestamp | Entity id | Level | Duplicates | Limits / cost | Rights | Backfill 2016–2026 |
|---|---|---|---|---|---|---|---|---|
| GDELT GKG 2.1 (BigQuery) | Feb 2015 → | 15-min batch, UTC (first-seen) | Organisation strings; noisy for ITC, LT | Document metadata + tone; titles in an extras field for many records (**unverified, test in pilot**) | Syndication heavy; dedup by URL/title | 1 TB/month free scan; table is multi-TB | Open with attribution; no article text | Feasible if queries are partitioned |
| NSE corporate announcements | Multi-year (depth untested) | Exact, IST, to the second | Symbol | Filing | Revisions as separate rows | Manual export | NSE terms; no automated collection | Feasible manually (10 symbols) |
| NewsAPI.org / NewsAPI.ai / Alpha Vantage / Finnhub | Free tiers ≈ 1 month or premium | Publisher | Query/ticker | Article | Yes | Paid for history | Storage restricted | Not free |
| Publisher RSS / archives | Current | Publisher | None | Article | Yes | - | Terms forbid stored corpora | No |
| GDELT DOC API | Rolling months | - | - | - | - | - | - | No |
| IN-FINews | Feb–Aug 2025 (claimed) | Unverified | Unverified | Article | ? | Free | Licence unread | No (7 months) |

**Proposed schema (`news_items`)**: `article_id` (hash of canonical URL), `source_system` (gdelt/nse/…), `publisher_domain`, `url`, `headline`, `text_repr` (headline or permitted summary only), `published_at_utc`, `first_seen_at_utc`, `retrieved_at_utc`, `source_timezone`, `available_at_ist`, `first_available_session` (from the calendar table: after 15:30 IST, weekend or holiday → next session), `entity_raw`, `ticker`, `mapping_confidence`, `scope` (company/market), `event_category`, `language`, `dup_group_id`, `is_duplicate`, `vader_compound`, `finbert_pos/neg/neu`, `model_name`, `model_revision`, `scored_at_utc`, `rights_note`, `retention_class`. Keys: `article_id` unique; (`ticker`,`article_id`) for the mapping table to avoid many-to-many joins; daily features keyed (`ticker`,`session`).

Feasibility is unknown until the pilot (T-108) measures coverage and precision. Decision D-11.

## H. FinBERT and VADER

* **VADER:** MIT licence; compound score in [−1, 1]; thresholds ±0.05; built for social-media text [WEB]. Use as the lexicon baseline on headlines.
* **FinBERT (`ProsusAI/finbert`):** the model card states CC BY-NC-SA 4.0, non-commercial; outputs positive/negative/neutral probabilities; fine-tuned on Financial PhraseBank [WEB]. Acceptable for an academic project; record licence and pin the revision hash (D-12).
* **Language:** English headlines only; Hindi/regional sources would need a multilingual model; out of scope unless the pilot shows English coverage is thin.
* **Unit:** headline-only (rights and 512-token limit); full text is not storable under publisher terms.
* **Scores:** FinBERT polarity = P(pos) − P(neg) plus the three probabilities; VADER compound.
* **Entity vs market:** company score = items mapped to the ticker; market score = items tagged market-wide or the cross-ticker mean; keep both.
* **Aggregation per (ticker, session):** deduplicate first; mean polarity, item count, share negative; 3-session momentum; volume-spike flag = count > rolling mean + 2 sd using past sessions only (PRD §10.1).
* **Time alignment:** by `first_available_session` only; items after 15:30 IST, on weekends or holidays go to the next session; no later edits or retrospective labels.
* **Ablation design:** identical rows, folds and model settings; arms = price-only, +VADER features, +FinBERT features; rows restricted to dates where news coverage exists for all arms; report ΔMAE and Δdirectional accuracy with paired bootstrap intervals; no assumption that sentiment helps (T-203).

## I. Universe and survivorship

* Identities (config, VERIFIED against bhavcopy symbols): BHARTIARTL, HDFCBANK, HINDUNILVR, ICICIBANK, INFY, ITC, LT, RELIANCE, SUNPHARMA, TCS; all present as `EQ` in every official file from 2019 to 2025; all have continuous history from 2016-01-01.
* Listing dates, historical name changes and index-membership dates: **not researched to primary sources in this audit** (all ten are long-listed; no rename observed in the window).
* The ten were chosen in 2026 from today's largest companies. A study on them alone is conditioned on survival and success. They do **not** represent the historical Indian equity universe.
* Point-in-time NIFTY 50 membership: only community reconstructions without licences [REPO]; official change circulars exist but are not compiled.
* **Recommendation (D-07):** treat the PRD's "8–15 liquid large-cap equities" as a **fixed, pre-declared case-study universe**; state in the report that results are conditional on stocks known in 2026 to be large and liquid, that the bias inflates buy-and-hold and equal-weight returns alike, and that no claim is made about other stocks. Task T-112.

## J. Features

Complete dictionary: `FEATURE_LABEL_DICTIONARY.csv` (35 rows covering raw columns, the 24 Mac features, the 24 GPU features, the Kaggle one-hot and the four labels).

* **J-1** Two different feature sets share file names (L-06). Experiment 01 used the GPU set + `Adj Close` (25 inputs).
* **J-2** Rolling windows are backward-looking and grouped by ticker (truncation test: 0 differing cells).
* **J-3** No target-derived column enters features (code and split report).
* **J-4** Scaling/imputation fit on training rows only; there are no cross-sectional transforms and no feature selection.
* **J-5** Look-ahead and level features: `adj_close_vs_close`, `Adj Close`, `sma_*`, `ema_*`, `macd`, `volume_sma_20` (L-02, L-03).
* **J-6** Same-day OHLCV is used, so the prediction time is **after the close of *t***. If a forecast were wanted before the close, same-day close/high/low/volume would be unavailable. Decision D-01.
* **J-7** PRD families not yet present in either set: Stochastic %K/%D, ROC, calendar (day-of-week, month, turn-of-month), index return/beta, yield spread, VIX level/change, volume z-score; ATR and OBV exist only in the GPU script; sequence length is 30 (PRD reference 60).
* **J-8** Naming/definition issues: `macd_signal_pct` is the histogram; RSI uses Wilder smoothing (the PRD listing uses a simple mean); `volume_change_1d` means different things in the two pipelines.

Tasks T-013, T-014, T-113.

## K. Labels and horizons

* Formulas (`build_next_day_dataset.py:21-33`, VERIFIED): `target_date_t1` = next row's date; `target_adj_close_t1` = next row's Adj Close; `target_log_return_t1` = ln(next/current); `target_direction_t1` = sign ∈ {−1, 0, +1}.
* Next *observed* session, not next *eligible* session: phantom and missing sessions distort 19 + ≈ 70 labels (L-14).
* Adjusted close as a label: defensible as a return basis; not defensible as a point-in-time level (§C). The PRD accepts "next-day adjusted close or next-day log return" (§3.4).
* Direction: 60 zero labels overall (53 in train+validation equities, 0.21 %); 19 of the 26 validation zeros are bad bars.
* Labels crossing corporate actions: 15 events; 13 benign; 2 artefacts (§C-3).
* Economic meaning: close-to-close return cannot be traded exactly by someone who decides after the close of *t*; state the execution assumption (D-01).

**Candidate multi-day horizons (not created; D-13):**

| h | Prediction time | Entry | Exit | Return | Overlap | Purge/embargo | Corporate actions | Costs |
|---|---|---|---|---|---|---|---|---|
| 1 | after close *t* | close *t* (or open *t+1*) | close *t+1* | ln(A[t+1]/A[t]) | none | none | 2 artefact labels | highest turnover |
| 5 | after close *t* | 〃 | close *t+5* | ln(A[t+5]/A[t]) | 4 of 5 days shared between consecutive labels | drop last 4 sessions before each boundary; evaluate on every 5th session or use overlap-robust errors | window may contain an ex-date: flag rows whose window contains CA-13/CA-15 | lower |
| 21 | after close *t* | 〃 | close *t+21* | ln(A[t+21]/A[t]) | 20 of 21 shared | drop last 20 sessions; ≈ 28 independent samples in validation | same; more windows affected | lowest; closest to the monthly literature in `RESEARCH_ROADMAP.md` |

## L. Leakage and validation

See `LEAKAGE_CODE_AUDIT.md` (19 findings with file, lines, severity, evidence, fix and test). Summary: split logic, label timing, train-only preprocessing and test isolation in code are correct; defects are L-01 (moving cut-off), L-02 (look-ahead feature), L-03 (restated levels), L-06/L-07 (two pipelines; executed code not in Git), L-08 (selection on reported validation in the committed deep script), L-13/L-14 (QA and calendar), L-17 (corrupt CPI CSV). **The final test partition has not been used for fitting, tuning or evaluation in anything inspected.**

## M. Data-integration architecture (proposal)

| Layer | Content | Key | Storage | Git |
|---|---|---|---|---|
| 1 Raw | Vendor/exchange/official files exactly as received, in `data/raw/<source>/<retrieved_utc>/` | file hash | local, immutable | manifest only |
| 2 Parsed | One tidy table per source, original units, `source_file`, `retrieved_at` | natural key of source | `data/interim/` | no |
| 3 Reference | Trading calendar; instrument master (symbol, ISIN history, listing date); corporate-action ledger; release-event tables (CPI, repo rate) | `date`; `isin`; `event_id` | `data/reference/` | **yes** (small, citable) |
| 4 Prices | Chosen basis (after D-02): raw, adjusted via ledger, flags | (`isin` or `ticker`, `session`) | `data/processed/<version>/` | no |
| 5 Context | Macro/market observations with `observed_for`, `available_from`, `vintage`, `status` | (`series_id`, `observed_for`, `vintage`) | 〃 | derived OK where licence allows |
| 6 News | `news_items`, mapping table, daily sentiment | `article_id`; (`ticker`,`session`) | 〃 | scores/metadata only |
| 7 Features | Feature panel from an allow-list | (`ticker`,`session`) | 〃 | no |
| 8 Labels | One table per horizon | (`ticker`,`session`,`h`) | 〃 | no |
| 9 Partitions | Frozen date boundaries + row keys | 〃 | 〃 | boundary config yes |
| 10 Model-ready | Join of 7–9 for an experiment id | 〃 | `data/model_ready/<exp>/` | no |

Rules: every dataset has a YAML sidecar (schema, source, retrieval time, timezone, licence, version, hash, transformation, QA report path); joins are only many-to-one onto (`ticker`,`session`) with `validate=` assertions; all release-timed data enters through one as-of join; outputs are versioned folders, never overwritten; one command rebuilds from the manifest; data stays out of Git, `data/MANIFEST.csv` and reference tables go in.

## N. Research design and experiment plan

**Relevance of the reviewed literature.** Gu–Kelly–Xiu and Fieberg et al. study *monthly cross-sectional* return prediction on thousands of stocks with firm characteristics. Transferable: chronological validation, train-only preprocessing, comparison with simple models, separation of forecast accuracy from portfolio results, attention to turnover. **Not transferable without a new experiment:** monthly horizon, pooled cross-sectional ranking, characteristic sets, rank-normalisation across a large cross-section (10 stocks is too few), any reported R² or Sharpe. The NIFTY paper (Fathali et al.) is an index-level, 2014–2018 study with unclear validation; use only as a tutorial reference. Copying a monthly method into the daily task would need an explicit, approved change of target.

**Assessment of Experiment 01 (as executed).** Sound structure (expanding folds, inner early-stopping split, refit, single scoring). Limitations: unfrozen data with 19 bad rows and two artefact labels; no hyper-parameter tuning (PRD requires tuning); one seed; `Adj Close` level as input; pooled deep vs per-ticker classical; summary = unweighted mean of per-(ticker, fold) rupee MAE, where LT and TCS contribute 41 % of the naive error and ITC 1.8 %; differences between top models and naive are 0.7–1.7 % of MAE without intervals; code not in Git. It is a valid *exploratory* result and should be labelled "Experiment 01 (exploratory, superseded data)". It is not evidence that the models are invalid, nor that the project is complete.

**Staged plan (tasks T-201…T-207, T-301…):**
1. Data and target integrity (Gates 1–2).
2. Naive baselines: zero-return (random walk), historical-mean return, always-up for direction.
3. Classical models, tuned with `TimeSeriesSplit` inside each training window.
4. Deep models, ≥ 5 seeds, same scored rows.
5. Macro/context ablation.
6. News/sentiment ablation (coverage-restricted rows for all arms).
7. Combined model.
8. Robustness: per ticker, per fold, event-window sensitivity, bootstrap intervals, Diebold–Mariano against naive.
9. Freeze → single final test.
10. Portfolio/backtest.

**Comparability rule:** two results are comparable only if dataset version, row set, label, folds and metric code are identical. Any change in rows (bad-bar repair, coverage restriction) makes it a new comparison; re-run the baseline on the new rows.

**Metrics:** return-space MAE/RMSE and skill vs naive per ticker (equal-weight average), PRD price metrics (RMSE, MAE, MAPE, R²) as secondary, directional accuracy on non-zero labels with the up-share shown, per-ticker and per-fold tables, intervals. Price-level R² (≈ 0.9 here even for the naive model) must not be presented as skill.

## O. Licensing, cost and governance

Per-source detail is in `DATA_SOURCE_MATRIX.csv` (columns cost, api_key, limits, licence_terms, storage_and_redistribution). Key points:

* **Yahoo/yfinance:** library Apache-2.0; data under Yahoo's terms; the project page says the API is for personal use and research/education [WEB]. Keep local; do not commit or publish raw data.
* **NSE:** terms prohibit systematic automated collection and restrict redistribution and simulation use [REPO]. `download_nse_bhavcopy.py` is automated collection of 5 files (and a second, unsaved script fetched 6 more). Low volume, but it should not be scaled up. Recommended position: manual exports, validation use, private storage (D-14).
* **MoSPI / RBI / FRED:** public official data, free; cite. FRED API and ALFRED need a free key.
* **GDELT:** open with attribution; BigQuery free tier 1 TB/month; costs accrue beyond it; requires a Google Cloud account.
* **FinBERT:** CC BY-NC-SA 4.0 (non-commercial). **VADER:** MIT.
* **News publishers:** no stored article corpora.
* **Private GitHub repo:** privacy does not create redistribution rights; commit manifests, reference tables built from public notices, and derived government-data tables only.
* No paid source is required for the recommended plan. No access-control bypass is recommended anywhere.

## P. Non-dataset PRD requirements (status)

| Requirement (PRD §) | Status | Note |
|---|---|---|
| Ingestion script, raw preserved (3) | Partial | Overwrites raw; no manifest |
| Cleaning pipeline + one-page quality report (4) | Partial | No calendar reindex, no outlier flags; QA misses real defects |
| Feature families incl. calendar, Stochastic, ROC, ATR, OBV, macro (5) | Partial | §J-7 |
| Sequence windows L, train-only scaling (5.3–5.4) | Implemented (notebook), untested in Git | L = 30 |
| EDA incl. ADF, QQ, JB, seasonality (6) | Not started | `notebooks/` empty |
| From-scratch finance maths; manual gradient-descent regression (7) | Not started | Missing from `docs/PRD_REQUIREMENTS.md` |
| Four tuned ML models under TimeSeriesSplit (8) | Partial | Trained once, untuned; code not in Git |
| Four DL architectures, early stopping, loss curves (9) | Partial | Trained; loss curves not saved; 1 layer vs PRD's 2-layer reference |
| Eight-model table on a genuine held-out window (9.5) | Not started | Validation-only so far |
| Sentiment module and with/without test (10) | Not started | No data |
| MPT, frontier, Ledoit-Wolf, Monte Carlo 20,000, caps (11) | Not started | |
| Backtest vs equal-weight and benchmark; risk metrics; bootstrap CI (7.6, 11.4) | Not started | |
| Transaction costs | Not started | PRD lists as a future enhancement; project documents require them |
| BUY/HOLD/SELL + rebalancing + hit-rate (12) | Not started | Principles agreed in `DECISIONS.md` |
| Abstention/no-trade | Not started | Principle agreed |
| Seven-panel Streamlit dashboard (13) | Not started | |
| config.yaml, pinned requirements, seeds (15.3) | Partial | JSON config; open version ranges |
| One-command rebuild / retrain (14.2) | Partial | GPU script rebuilds data; no train command for the executed experiment |
| 10–15 page report (14.2) | Not started | |

`docs/PRD_REQUIREMENTS.md` omits at least 12 PRD items (T-021).

## Q. External sources consulted on 2026-11-14 (WEB)

| Claim supported | Source | Quality |
|---|---|---|
| NSE/BSE closed 15 Jan 2026 (Maharashtra civic polls) | Angel One notice https://www.angelone.in/announcements/market/trading-holiday-on-15-jan-2026-on-account-of-municipal-elections-in-maharashtra ; Business Today https://www.businesstoday.in/markets/stocks/story/stock-market-holiday-are-nse-bse-open-or-closed-on-thursday-january-15-510969-2026-01-15 | Secondary (broker/news relaying the exchange circular; circular itself not fetched) |
| 18 Mar 2025 was a normal session; NIFTY 22,834.30 | Business Standard https://www.business-standard.com/markets/news/stock-market-live-updates-sensex-today-nifty-today-march-18-bse-nse-bajaj-finserv-pdp-shipping-ipo-125031800081_1.html | Secondary |
| Special sessions 20 Jan, 2 Mar, 18 May 2024 | Business Standard https://www.business-standard.com/markets/news/nse-to-run-special-trading-session-on-may-18-with-disaster-recovery-switch-124050701155_1.html ; The Week https://www.theweek.in/news/biz-tech/2024/02/14/nse-to-hold-special-trading-session-on-march-2-saturday-heres-the-reason.html ; Angel One https://www.angelone.in/news/share-market/nse-special-live-session-on-january-20-2024 | Secondary |
| Trading announced for Sunday 1 Feb 2026 | Business Today https://www.businesstoday.in/union-budget/story/union-budget-2026-nse-bse-declare-sunday-trading-schedule-fo-and-commodities-also-open-511251-2026-01-16 | Secondary; pre-event |
| ITC 6 Jan 2025: prior close ≈ ₹481.6, discovered ₹455.6, close ₹442.65 | Upstox, Business Standard (URLs in `CORPORATE_ACTION_AUDIT.md`) | Secondary; sources disagree on the closing change |
| HUL 5 Dec 2025 demerger effect; KWIL listing ≈ ₹29.8, "26 % below indicative" | Business Standard, Upstox (URLs there) | Secondary; indicative price not found |
| BHARTIARTL 2021 rights partly paid (₹133.75 on application) | Letter of Offer copy https://business.bofa.com/content/dam/flagship/in/en/investment-banking/Bharti-Airtel-Limited-Letter-of-Offer--2021.pdf ; BSE filing https://bseindia.com/xml-data/corpfiling/AttachHis/288aad01-8f6a-40a8-8044-ac8d03defeb1.pdf | Primary (via search summary; documents not read in full) |
| FinBERT licence CC BY-NC-SA 4.0 | https://huggingface.co/ProsusAI/finbert | Primary |
| VADER MIT licence, thresholds | https://github.com/cjhutto/vaderSentiment | Primary |
| yfinance licence and personal-use note | https://github.com/ranaroussi/yfinance | Primary |

All other external statements are **REPO** (taken from `docs/DATA_RESEARCH.md` with the URLs recorded there and in `DATA_SOURCE_MATRIX.csv`) and were not re-fetched.

## R. Task register

All 52 tasks with ID, category, priority, status, description, reason, proposed implementation, dependencies, input/output files, acceptance criteria, effort, approval flag, blocker and evidence reference are in `REMAINING_TASKS.csv` (and `.json`), sorted by priority then dependency. Counts: P0 22, P1 17, P2 7, P3 6. Status: not started 29; requires user decision 9; partially implemented 5; researched but not implemented 5; blocked 2; implemented but untested 2.

| P0 task | One-line description | Approval |
|---|---|---|
| T-001 | Sync local clone with GitHub | yes |
| T-002 | Rescue Kaggle results, checkpoints and code | yes |
| T-003 | Correct four inaccurate document statements | yes |
| T-004 | Immutable hashed raw snapshot + manifest | yes |
| T-005 | Freeze split dates | decision D-04 |
| T-006 | Approve price basis and target | decision D-02 |
| T-007 | Official trading-calendar table | no |
| T-008 | Remove phantom rows, repair stale bars | decision D-05 |
| T-009 | Special-session policy | decision D-06 |
| T-010 | Complete, primary-source the action ledger | no |
| T-011 | Event-window official prices for 5 events | yes |
| T-012 | Full-history official reconciliation | decision D-14 |
| T-013 | Remove look-ahead and level features | yes |
| T-014 | Merge the two pipelines | yes |
| T-015 | Commit notebook-only fixes | yes |
| T-016 | Test suite and runnable pytest | no |
| T-017 | Data-rights register and ignore rules | yes |
| T-018 | Repair CPI CSVs and housekeeping | yes |
| T-019 | Pin dependencies | no |
| T-020 | Freeze evaluation protocol | decision D-17 |
| T-021 | PRD traceability matrix; store PRD | yes |
| T-022 | Deadline/scope decision | decision D-15 |

## S. Acceptance criteria of this audit

| # | Criterion | Result |
|---|---|---|
| 1 | Every relevant documentation file read | **Partly**: three long files read in part (§1) |
| 2 | Every data/training script inspected | Yes, plus the notebook |
| 3 | Local data folders inventoried | Yes (77 entries) |
| 4 | Claims classified | Yes (§2) |
| 5 | CPI pipeline checked against files and code | Yes |
| 6 | Yahoo/NSE basis addressed with evidence and gaps | Yes |
| 7 | Evidence-backed event ledger | Yes, 17 rows; 7 rows lack primary evidence; completeness open |
| 8 | Macro, context, fundamentals, news sources researched | Yes, mainly by consolidating repo research; limited fresh verification (§Q) |
| 9 | Sentiment feasibility assessed | Yes; depends on pilot |
| 10 | Survivorship assessed | Yes; listing/membership dates not primary-sourced |
| 11 | Feature and label definitions documented | Yes |
| 12 | Leakage inspected in code | Yes |
| 13 | Licensing and costs considered | Yes |
| 14 | Every task has priority, dependency, acceptance criterion | Yes |
| 15 | Ten deliverables created | Yes |
| 16 | No original data, labels, splits or model outputs changed | Yes |
| 17 | Final test untouched | Yes (structural read only; disclosed) |
| 18 | Reviewable without conversation context | Intended; scripts and evidence included |

**Not everything is complete:** criteria 1, 7, 8 and 10 are met only with the stated limitations.

## T. Deliberately not done

No retraining; no test evaluation; no change to scripts, data, labels, splits, PRD, universe or documents; no `git pull`/commit/push; no new data downloads (NSE, GDELT, RBI, FRED, news); no application to NSE; no contact with any third party; no opening of `cpi_33.xlsx`; no investigation of test-period price moves beyond flagging one row; no verification of dividend amounts; no primary-source check of seven bonus/split events, listing dates or pre-2024 special sessions.

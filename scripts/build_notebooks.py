"""Build and execute the two analysis notebooks (PRD sections 6 and 7).

Usage: python scripts/build_notebooks.py

Writes notebooks/01_eda.ipynb and notebooks/02_finance_math_verification.ipynb with
outputs. Both use ONLY the training period (sessions up to 2023-12-29), so nothing they
show can leak validation or held-out test information into modelling choices.
Requires: statsmodels, matplotlib, nbformat, nbclient, ipykernel.
"""
from __future__ import annotations
import os
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"

SETUP = r'''
import os, sys, warnings
os.environ.setdefault("OMP_NUM_THREADS", "1")
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy import stats
pd.set_option("display.width", 160); pd.set_option("display.precision", 4)
PAL = ["#2B6CB0", "#C2571A", "#7B4FA6", "#2F8F6B"]; INK, GRID, PAPER = "#1C1B19", "#E4DFD5", "#FAF8F4"
plt.rcParams.update({"figure.facecolor": PAPER, "axes.facecolor": PAPER, "axes.edgecolor": "#8C867A", "axes.grid": True,
                     "grid.color": GRID, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
                     "axes.titlesize": 10, "figure.dpi": 90, "axes.prop_cycle": plt.cycler(color=PAL)})
TRAIN_END = pd.Timestamp("2023-12-29")   # last feature date of the training partition
panel = pd.read_csv(ROOT / "data/processed/market_panel.csv", parse_dates=["Date"])
panel = panel[panel.Date <= TRAIN_END]   # validation and test periods are excluded
px = panel.pivot(index="Date", columns="Ticker", values="Adj Close")
vol = panel.pivot(index="Date", columns="Ticker", values="Volume")
r = np.log(px).diff().iloc[1:]
EQ = [c for c in px.columns if c != "^NSEI"]
short = lambda t: t.replace(".NS", "").replace("^NSEI", "NIFTY 50")
print(f"Training period: {px.index.min():%d %b %Y} to {px.index.max():%d %b %Y}; {len(px)} sessions; {len(EQ)} stocks + NIFTY 50")
'''

EDA = [
("md", """# Exploratory data analysis (PRD section 6)

**Data:** daily adjusted closes and volumes for ten NSE stocks and the NIFTY 50 price index (Yahoo Finance; local build in `data/processed/market_panel.csv`).
**Scope:** the **training period only** (1 Jan 2016 to 29 Dec 2023). Validation (2024 to May 2026) and the sealed test window (May to Nov 2026) are deliberately excluded so these findings can inform modelling choices without leaking later information.
**Caveat:** Yahoo prices are back-adjusted for later corporate actions, so price *levels* are not the prices quoted at the time; returns are reliable (see `reports/claude_dataset_audit_2026-11-14/CORPORATE_ACTION_AUDIT.md`). The 19 stale or phantom rows found by the audit fall after this period."""),
("code", SETUP),
("md", "## 1. Price trends with 50- and 200-session moving averages, and volume"),
("code", r'''
for t in px.columns:
    fig, (a, b) = plt.subplots(2, 1, figsize=(9, 3.2), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    s = px[t]; a.plot(s.index, s, color=PAL[0], lw=1, label="Adjusted close")
    a.plot(s.index, s.rolling(50).mean(), color=PAL[1], lw=1, label="50-session MA"); a.plot(s.index, s.rolling(200).mean(), color=PAL[2], lw=1, label="200-session MA")
    a.set_yscale("log"); a.set_title(f"{short(t)}: adjusted close (log scale)"); a.legend(loc="upper left", frameon=False, fontsize=8)
    if t == "^NSEI":
        b.text(0.5, 0.5, "Index volume from Yahoo is not reliable; not shown", ha="center", va="center", transform=b.transAxes, color="#6B665C")
    else:
        b.bar(vol.index, vol[t].rolling(20).mean() / 1e6, width=1.5, color="#8C867A"); b.set_ylabel("vol, m (20d avg)")
    plt.tight_layout(); plt.show()
'''),
("md", """**Finding.** Every series trends upward over 2016–2023 with a deep, synchronised fall in March 2020 and long stretches above and below the 200-session average. Levels differ by more than an order of magnitude between stocks.
**Consequence.** Raw prices are trending and scale-dependent, so they are a poor modelling target and a poor pooled feature. Models predict next-session *log returns*, and most features are ratios to moving averages rather than price levels."""),
("md", "## 2. Stationarity: Augmented Dickey-Fuller test on log price versus log return"),
("code", r'''
from statsmodels.tsa.stattools import adfuller
adf = pd.DataFrame({short(t): {"ADF p-value, log price": adfuller(np.log(px[t].dropna()))[1],
                                "ADF p-value, log return": adfuller(r[t].dropna())[1]} for t in px}).T
adf["Price stationary at 5%?"] = adf["ADF p-value, log price"] < 0.05
adf["Return stationary at 5%?"] = adf["ADF p-value, log return"] < 0.05
display(adf.round(4))
print(f"Log prices: unit root NOT rejected for {(~adf['Price stationary at 5%?']).sum()} of {len(adf)} series. "
      f"Log returns: unit root rejected for {adf['Return stationary at 5%?'].sum()} of {len(adf)}.")
'''),
("md", """**Finding.** For all eleven series the ADF test cannot reject a unit root in log prices (p between about 0.36 and 0.95), and strongly rejects it for log returns.
**Consequence.** This is the empirical justification for forecasting returns rather than prices, and for evaluating price forecasts against the naive random-walk baseline, which is the correct benchmark for a non-stationary price."""),
("md", "## 3. Return distributions: histograms with a normal overlay, QQ plots, skewness and kurtosis"),
("code", r'''
fig, axes = plt.subplots(3, 4, figsize=(11, 7)); axes = axes.ravel()
for ax, t in zip(axes, px.columns):
    x = r[t].dropna(); ax.hist(x, bins=80, density=True, color=PAL[0], alpha=0.7)
    g = np.linspace(x.min(), x.max(), 300); ax.plot(g, stats.norm.pdf(g, x.mean(), x.std()), color=PAL[1], lw=1.2)
    ax.set_title(short(t)); ax.set_xlim(-0.12, 0.12)
axes[-1].axis("off"); fig.suptitle("Daily log returns (bars) against a normal distribution with the same mean and standard deviation (line)", fontsize=10)
plt.tight_layout(); plt.show()
fig, axes = plt.subplots(3, 4, figsize=(11, 7)); axes = axes.ravel()
for ax, t in zip(axes, px.columns):
    (osm, osr), (sl, ic, _) = stats.probplot(r[t].dropna(), dist="norm")
    ax.scatter(osm, osr, s=3, color=PAL[0]); ax.plot(osm, sl * osm + ic, color=PAL[1], lw=1); ax.set_title(f"QQ: {short(t)}")
axes[-1].axis("off"); plt.tight_layout(); plt.show()
dist = pd.DataFrame({short(t): {"mean (daily %)": r[t].mean() * 100, "std (daily %)": r[t].std() * 100, "skewness": stats.skew(r[t].dropna()),
                                 "excess kurtosis": stats.kurtosis(r[t].dropna()), "Jarque-Bera p": stats.jarque_bera(r[t].dropna()).pvalue} for t in px}).T
display(dist.round(4))
'''),
("md", """**Finding.** Excess kurtosis ranges from about 4 to 23 (the index is highest, driven by March 2020) and the Jarque-Bera test rejects normality for every series with p effectively zero. Skewness is mixed in sign; the index is clearly negatively skewed. QQ plots bend away from the line in both tails.
**Consequence.** Risk must not assume normality: the dashboard reports historical (empirical) VaR and maximum drawdown alongside volatility, and the deep models use a Huber loss, which is less sensitive to extreme returns than squared error."""),
("md", "## 4. Correlation of daily returns (Pearson and Spearman)"),
("code", r'''
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, method in zip(axes, ["pearson", "spearman"]):
    c = r[EQ].corr(method=method); im = ax.imshow(c, vmin=0, vmax=1, cmap="Blues")
    ax.set_xticks(range(len(EQ)), [short(t) for t in EQ], rotation=60, ha="right"); ax.set_yticks(range(len(EQ)), [short(t) for t in EQ])
    for i in range(len(EQ)):
        for j in range(len(EQ)):
            ax.text(j, i, f"{c.iloc[i, j]:.2f}", ha="center", va="center", fontsize=6.5, color="white" if c.iloc[i, j] > 0.6 else INK)
    ax.set_title(f"{method.title()} correlation"); ax.grid(False)
plt.colorbar(im, ax=axes, fraction=0.025); plt.show()
c = r[EQ].corr(); off = c.where(np.triu(np.ones(c.shape), 1).astype(bool)).stack()
print(f"Average pairwise Pearson correlation {off.mean():.2f} (range {off.min():.2f} to {off.max():.2f}); highest pair: {short(off.idxmax()[0])}-{short(off.idxmax()[1])}.")
display(r.corr()["^NSEI"].drop("^NSEI").rename(index=short).rename("correlation with NIFTY 50").to_frame().round(2))
'''),
("md", """**Finding.** Correlations are positive but moderate (average about 0.28), highest within sectors (Infosys–TCS about 0.58, HDFC Bank–ICICI Bank about 0.5). The banks and Larsen & Toubro move most with the index; Sun Pharma and Bharti Airtel least. Rank (Spearman) and linear (Pearson) correlations tell the same story.
**Consequence.** There is real diversification across the ten names, but sector pairs overlap. The optimiser therefore uses a shrunk (Ledoit-Wolf) covariance and a 30% per-stock cap to avoid concentrating in near-duplicates."""),
("md", "## 5. Volatility regimes and clustering, with India VIX"),
("code", r'''
rv = r.rolling(21).std() * np.sqrt(252) * 100
vix_path = ROOT / "data/processed/market_context/market_context_panel.csv"
fig, ax = plt.subplots(figsize=(10, 3.4))
ax.plot(rv.index, rv["^NSEI"], color=PAL[0], lw=1, label="NIFTY 50 realised volatility (21 sessions, annualised %)")
if vix_path.exists():
    ctx = pd.read_csv(vix_path, parse_dates=["Date"]); vix = ctx[(ctx.Ticker == "^INDIAVIX") & (ctx.Date <= TRAIN_END)].set_index("Date").Close
    ax.plot(vix.index, vix, color=PAL[1], lw=1, label="India VIX (implied, annualised %)")
    j = pd.concat([rv["^NSEI"], vix], axis=1).dropna(); print(f"Correlation of NIFTY realised volatility with India VIX: {j.corr().iloc[0, 1]:.2f}")
else:
    print("India VIX not downloaded (scripts/download_market_context.py); realised volatility only.")
ax.legend(frameon=False, fontsize=8); ax.set_title("Volatility regimes: both measures share one unit (annualised %)"); plt.show()
fig, ax = plt.subplots(figsize=(10, 3.2))
for t in EQ: ax.plot(rv.index, rv[t], lw=0.6, alpha=0.6)
ax.set_title("Rolling 21-session volatility, all ten stocks (annualised %)"); plt.show()
lags = range(1, 21)
acf = pd.DataFrame({"returns": [r[EQ].apply(lambda s: s.autocorr(k)).mean() for k in lags],
                    "absolute returns": [r[EQ].abs().apply(lambda s: s.autocorr(k)).mean() for k in lags]}, index=lags)
ax = acf.plot.bar(figsize=(10, 3), color=[PAL[0], PAL[1]], width=0.8); ax.axhline(0, color=INK, lw=0.8)
ax.set_title("Average autocorrelation across stocks by lag (sessions)"); plt.show()
print(f"Mean lag-1 autocorrelation: returns {acf.loc[1, 'returns']:+.3f}, absolute returns {acf.loc[1, 'absolute returns']:+.3f}")
'''),
("md", """**Finding.** Volatility comes in regimes: calm 2017, stressed 2020, then a gradual decline. Realised NIFTY volatility tracks India VIX closely (correlation about 0.86). Returns themselves are almost uncorrelated from one day to the next (average lag-1 autocorrelation close to zero), but *absolute* returns are clearly autocorrelated over many lags: large moves cluster.
**Consequence.** The level of tomorrow's return is hard to predict from past returns, which is consistent with the models failing to beat the naive forecast, while the *size* of moves is predictable. Rolling volatility features are therefore included, and risk is measured over recent windows rather than full-history averages."""),
("md", "## 6. Seasonality: month and day of week, and an STL decomposition"),
("code", r'''
ew = r[EQ].mean(axis=1)   # equal-weight daily log return of the ten stocks
heat = ew.groupby([ew.index.year, ew.index.month]).sum().unstack() * 100
fig, ax = plt.subplots(figsize=(10, 3.4)); im = ax.imshow(heat, cmap="RdBu", vmin=-15, vmax=15, aspect="auto")
ax.set_xticks(range(12), ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]); ax.set_yticks(range(len(heat)), heat.index)
for i in range(heat.shape[0]):
    for j in range(heat.shape[1]):
        v = heat.iloc[i, j]
        if pd.notna(v): ax.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=7)
ax.grid(False); ax.set_title("Equal-weight monthly log return by year (%)"); plt.colorbar(im, ax=ax, fraction=0.02); plt.show()
wd = ew[ew.index.dayofweek < 5]
dow = wd.groupby(wd.index.dayofweek).agg(["mean", "std", "count"]); dow.index = ["Mon", "Tue", "Wed", "Thu", "Fri"]
dow["t-stat"] = dow["mean"] / (dow["std"] / np.sqrt(dow["count"])); dow["mean"] *= 100; dow["std"] *= 100
display(dow.rename(columns={"mean": "mean (daily %)", "std": "std (daily %)"}).round(3))
from statsmodels.tsa.seasonal import STL
m = np.log(px["^NSEI"]).resample("ME").last()
res = STL(m, period=12, robust=True).fit()
fig, axes = plt.subplots(3, 1, figsize=(10, 5), sharex=True)
for ax, (name, s) in zip(axes, [("trend", res.trend), ("seasonal", res.seasonal), ("residual", res.resid)]):
    ax.plot(s.index, s, color=PAL[0], lw=1); ax.set_title(f"NIFTY 50 monthly log level: {name}")
plt.tight_layout(); plt.show()
print(f"Seasonal component amplitude: {(res.seasonal.max() - res.seasonal.min()) * 100:.1f}% of index level; residual standard deviation {res.resid.std() * 100:.1f}%.")
'''),
("md", """**Finding.** No month is consistently positive or negative across years; the heatmap is dominated by year-specific events (2020). Among weekdays only Tuesday's mean is statistically distinguishable from zero on its own (t about 3.4), but with five days tested on one eight-year sample this is weak evidence and could be chance. STL assigns the index a seasonal swing of roughly 12% of its level, larger than the residual, yet the month-by-year heatmap shows that no month is consistently positive or negative; with only eight observations per calendar month, this pattern cannot be distinguished from a few large years (notably 2020).
**Consequence.** No calendar features were added. Any seasonal effect would need to be confirmed out of sample before it is used."""),
("md", """## Summary of decisions informed by this analysis

| Finding | Decision |
|---|---|
| Prices non-stationary, returns stationary (ADF) | Predict next-session log returns; benchmark against the naive random walk |
| Fat tails, non-normal returns | Empirical VaR and drawdown in risk reporting; Huber loss for deep models |
| Moderate, sector-clustered correlations | Ledoit-Wolf covariance and a 30% cap in optimisation |
| Volatility clustering; VIX tracks realised volatility | Rolling volatility features; recent-window risk measures |
| Little predictable autocorrelation in returns | Expect a hard-to-beat naive baseline (confirmed in validation) |
| No seasonality that is consistent across years | No calendar features |

All statistics above use the training period only."""),
]

FIN = [
("md", """# Financial mathematics verification (PRD section 7)

The project's own implementations in `src/northgate/finance.py` and the manual gradient-descent regression in `src/northgate/models/gradient_descent.py` are checked against independent library calculations on real data from the **training period only** (2016–2023). A difference at floating-point precision (around 1e-12 or smaller) means the hand-written formula is correct."""),
("code", SETUP),
("md", "## 1. Returns, risk and portfolio measures: scratch versus library"),
("code", r'''
from northgate import finance as FN
pxs = px[EQ]; sr = pxs.pct_change().iloc[1:]; m = px["^NSEI"].pct_change().iloc[1:]; s = sr["RELIANCE.NS"]; rf = 0.065
w = pd.Series(1 / len(EQ), index=EQ); port = (sr * w).sum(axis=1)
def mdd_alt(x):
    v = np.cumprod(1 + x.values); return float((v / np.maximum.accumulate(v) - 1).min())
ex = s - rf / 252
rows = [
 ("Simple returns (max abs diff)", float((FN.simple_returns(pxs).iloc[1:] - pxs.pct_change().iloc[1:]).abs().max().max()), 0.0),
 ("Log returns (max abs diff)", float((FN.log_returns(pxs).iloc[1:] - np.log1p(pxs.pct_change().iloc[1:])).abs().max().max()), 0.0),
 ("Annualised mean return, RELIANCE", FN.annualise_mean(s), float(np.mean(s) * 252)),
 ("Annualised volatility, RELIANCE", FN.annualise_vol(s), float(np.std(s, ddof=1) * np.sqrt(252))),
 ("Covariance matrix (max abs diff)", float(np.abs(FN.covariance(sr).to_numpy() - np.cov(sr.to_numpy().T, ddof=1)).max()), 0.0),
 ("Correlation from covariance, RELIANCE-HDFCBANK", float(FN.covariance(sr).loc["RELIANCE.NS", "HDFCBANK.NS"] / (sr["RELIANCE.NS"].std() * sr["HDFCBANK.NS"].std())), float(sr["RELIANCE.NS"].corr(sr["HDFCBANK.NS"]))),
 ("Beta, RELIANCE vs NIFTY 50 (common dates)", FN.beta(s, m), float(np.polyfit(*pd.concat([m, s], axis=1).dropna().to_numpy().T, 1)[0])),
 ("Sharpe ratio, RELIANCE (rf 6.5%)", FN.sharpe(s, rf), float(ex.mean() / ex.std() * np.sqrt(252))),
 ("Sortino ratio, RELIANCE", FN.sortino(s, rf), float(ex.mean() / np.sqrt(np.mean(np.minimum(ex, 0) ** 2)) * np.sqrt(252))),
 ("Maximum drawdown, RELIANCE", FN.max_drawdown(s), mdd_alt(s)),
 ("Historical VaR 95%, RELIANCE", FN.var_historical(s), float(np.percentile(s, 5))),
 ("Calmar ratio, RELIANCE", FN.calmar(s), float(((1 + s).prod() ** (252 / len(s)) - 1) / abs(mdd_alt(s)))),
 ("Portfolio variance w'Σw vs variance of portfolio returns", float(w @ FN.covariance(sr) @ w), float(np.var(port, ddof=1))),
]
check = pd.DataFrame(rows, columns=["Quantity", "Northgate (scratch)", "Library / independent"])
check["Absolute difference"] = (check.iloc[:, 1] - check.iloc[:, 2]).abs()
display(check.style.format({"Northgate (scratch)": "{:.10f}", "Library / independent": "{:.10f}", "Absolute difference": "{:.2e}"}))
print("Largest absolute difference:", f"{check['Absolute difference'].max():.2e}")
'''),
("md", """**Result.** Every hand-written quantity matches its independent counterpart to floating-point precision. The definitions used throughout the dashboard are: simple return (P_t − P_{t−1})/P_{t−1}; log return ln(P_t/P_{t−1}); annualisation ×252 for means and ×√252 for volatility; Sharpe (μ − r_f)/σ; Sortino with downside deviation; maximum drawdown min(V_t / max V − 1); historical VaR as the 5th percentile; Calmar as CAGR / |maximum drawdown|; portfolio variance wᵀΣw."""),
("md", "## 2. Optimisation check: manual gradient descent versus closed-form OLS"),
("code", r'''
from northgate import features as F
from northgate.models.gradient_descent import gd_linreg, ols_closed_form
from sklearn.linear_model import LinearRegression
feat = F.partition(F.add_labels(F.build(pd.read_csv(ROOT / "data/processed/market_panel.csv", parse_dates=["Date"]))), "train")
d = feat[feat.Ticker == "RELIANCE.NS"].dropna(subset=[F.TARGET])
cols = ["return_1d", "return_5d", "price_sma_ratio_20", "volatility_20d", "rsi_14"]
d = d.replace([np.inf, -np.inf], np.nan).dropna(subset=cols); X = d[cols].to_numpy(); X = (X - X.mean(0)) / X.std(0); y = d[F.TARGET].to_numpy()
w_gd, b_gd, hist = gd_linreg(X, y, lr=0.1, epochs=20000, tol=0.0)
w_ols, b_ols = ols_closed_form(X, y); sk = LinearRegression().fit(X, y)
coef = pd.DataFrame({"gradient descent": np.r_[b_gd, w_gd], "closed-form OLS": np.r_[b_ols, w_ols], "scikit-learn": np.r_[sk.intercept_, sk.coef_]},
                    index=["intercept"] + cols)
coef["|GD - OLS|"] = (coef["gradient descent"] - coef["closed-form OLS"]).abs()
display(coef.style.format("{:.3e}"))
print(f"Converged in {len(hist)} epochs; max |GD - OLS| = {coef['|GD - OLS|'].max():.2e}; training R² = {sk.score(X, y):.4f} on {len(y)} rows")
fig, ax = plt.subplots(figsize=(8, 2.8)); ax.plot(hist, color=PAL[0]); ax.set_yscale("log"); ax.set_xlabel("epoch"); ax.set_ylabel("mean squared error")
ax.set_title("Gradient-descent loss (RELIANCE, training period, 5 standardised features)"); plt.show()
'''),
("md", """**Result.** Gradient descent converges to the same coefficients as the normal-equation solution and scikit-learn (the largest difference is printed above), confirming the update rule θ ← θ − η∇L. The fitted regression explains almost none of the variance in next-session returns (training R² near zero), which agrees with the EDA finding of negligible return autocorrelation and with the validation result that no model beat the naive forecast."""),
]


def build(cells, path: Path) -> None:
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_markdown_cell(c.strip()) if k == "md" else nbformat.v4.new_code_cell(c.strip()) for k, c in cells]
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(OUT)}}).execute()
    nbformat.write(nb, path)
    print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    OUT.mkdir(exist_ok=True)
    build(EDA, OUT / "01_eda.ipynb")
    build(FIN, OUT / "02_finance_math_verification.ipynb")

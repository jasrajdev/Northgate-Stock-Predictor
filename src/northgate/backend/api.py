"""Facade used by the dashboard. Functions return plain DataFrames / dicts / dataclasses so the
same calls can sit behind an HTTP API later. Nothing here trains a model or downloads data.
"""
from __future__ import annotations
from functools import lru_cache
import numpy as np
import pandas as pd
from .. import config, finance as FN, recommend as R
from . import experiments, inference, market, risk

DataUnavailable = market.DataUnavailable
InferenceUnavailable = inference.InferenceUnavailable
TD = FN.TD


def cfg() -> dict:
    return config.recommendation()


# ---------------- market ----------------
def tickers(include_benchmark: bool = False) -> list[str]:
    return market.tickers(include_benchmark)


def names() -> dict:
    return market.names()


def overview() -> dict:
    p = market.load_panel()
    eq = p[p.Ticker != market.BENCHMARK]; suspect = eq[eq.suspect_bar]
    g = p.groupby("Ticker")["Adj Close"]
    last = p.groupby("Ticker").tail(1).set_index("Ticker")
    def trailing(n):
        return g.apply(lambda s: s.iloc[-1] / s.iloc[-(n + 1)] - 1 if len(s) > n else np.nan)
    spark = p.groupby("Ticker").apply(lambda x: x["Adj Close"].tail(63).round(2).tolist(), include_groups=False)
    table = pd.DataFrame({"Name": last.Name, "Last session": last.Date.dt.date, "Close": last.Close,
                          "1 session": trailing(1), "1 month (21)": trailing(21), "1 year (252)": trailing(252),
                          "3 months": spark, "Sessions held": p.groupby("Ticker").size()})
    return {"first_date": p.Date.min(), "last_date": p.Date.max(), "rows": len(p), "n_equities": eq.Ticker.nunique(),
            "table": table, "suspect_rows": len(suspect), "suspect_dates": sorted(suspect.Date.dt.strftime("%Y-%m-%d").unique()),
            "train_end": config.TRAIN_TARGET_END, "validation_end": config.VALIDATION_TARGET_END}


def stock_history(ticker: str) -> pd.DataFrame:
    p = market.load_panel(); f = market.load_features()
    cols = ["Date", "Ticker", "sma_20", "sma_50", "rsi_14", "volatility_20d", "bollinger_width_20", "volume_to_sma_20", "log_return_1d"]
    return p[p.Ticker == ticker].merge(f.loc[f.Ticker == ticker, [c for c in cols if c in f.columns]], on=["Date", "Ticker"], how="left").reset_index(drop=True)


def market_context() -> dict:
    """India VIX, sector indices (Yahoo) and FRED macro series, if downloaded. Not point-in-time."""
    out = {"available": False}
    c = config.PROCESSED / "market_context" / "market_context_panel.csv"
    m = config.PROCESSED / "macro_context" / "macro_observation_panel.csv"
    if c.exists():
        ctx = pd.read_csv(c, parse_dates=["Date"]); out.update(available=True, context=ctx)
    if m.exists():
        out["macro"] = pd.read_csv(m, parse_dates=["observation_date"]).dropna(subset=["value"])
    return out


# ---------------- risk ----------------
def risk_summary(start=None, end=None) -> pd.DataFrame:
    return risk.summary(start, end)


def drawdown_series(ticker: str) -> pd.Series:
    return risk.drawdown(risk.returns_wide()[ticker].dropna())


def rolling_volatility(ticker: str, window: int = 20) -> pd.Series:
    return risk.rolling_volatility(ticker, window)


def correlation(start=None, end=None) -> pd.DataFrame:
    return risk.correlation(start, end)


# ---------------- models ----------------
def experiment_available() -> bool:
    return experiments.available()


def experiment() -> dict:
    d = dict(experiments.load()); d["overall"] = experiments.overall_vs_baselines(); d["by_fold"] = experiments.folds_vs_baselines()
    d["naive"], d["always_up"] = experiments.NAIVE, experiments.ALWAYS_UP
    return d


def local_classical_validation() -> pd.DataFrame | None:
    p = config.MODELS / "classical" / "validation_summary.csv"
    return pd.read_csv(p) if p.exists() else None


def registry():
    return inference.registry()


def forecasts(model: str | None = None) -> pd.DataFrame:
    reg = registry(); model = model or reg.selected
    if model is None:
        raise InferenceUnavailable("No model is available for inference.")
    return inference.predict_latest(model)


def all_forecasts() -> pd.DataFrame:
    return inference.all_forecasts()


def validation_path(model: str, ticker: str) -> pd.DataFrame:
    return inference.validation_path(model, ticker)


def error_band(model: str, ticker: str):
    return inference.error_band(model, ticker)


# ---------------- sentiment ----------------
def sentiment() -> dict:
    s, d = config.PROCESSED / "news_scored.csv", config.PROCESSED / "sentiment_daily.csv"
    if not (s.exists() and d.exists()):
        return {"available": False}
    items = pd.read_csv(s, parse_dates=["session"]); daily = pd.read_csv(d, parse_dates=["session"])
    return {"available": True, "items": items, "daily": daily, "score_source": str(daily["score_source"].iloc[0])}


def sentiment_signal(as_of: pd.Timestamp) -> dict:
    """Mean score over the last N sessions up to and including `as_of`, per ticker (None if too few articles)."""
    s = sentiment()
    if not s["available"]:
        return {}
    c = cfg(); d = s["daily"]; d = d[d.session <= as_of]
    out = {}
    for t, g in d.groupby("ticker"):
        g = g.sort_values("session").tail(c["sentiment_lookback_sessions"])
        if g.articles.sum() >= c["sentiment_min_articles"]:
            out[t] = float(np.average(g.score, weights=g.articles))
    return out


# ---------------- portfolio ----------------
@lru_cache(maxsize=1)
def equity_returns() -> pd.DataFrame:
    return risk.returns_wide().drop(columns=[market.BENCHMARK]).iloc[1:]


def example_holdings() -> pd.DataFrame:
    """Illustrative holdings: equal rupee amount per stock at the latest close. Editable in the app."""
    last = market.load_panel().groupby("Ticker").tail(1).set_index("Ticker")
    notional = cfg()["example_portfolio_notional_per_stock_inr"]
    return pd.DataFrame({"Shares": (notional // last.loc[tickers(), "Close"]).astype(int)})


def value_holdings(holdings: pd.DataFrame) -> pd.DataFrame:
    p = market.load_panel()
    last2 = p[p.Ticker.isin(holdings.index)].groupby("Ticker").tail(2)
    prev = last2.groupby("Ticker").Close.first(); last = last2.groupby("Ticker").Close.last()
    df = holdings.copy(); df["Price"] = last; df["Value"] = df.Shares * df.Price
    df["Day change"] = df.Shares * (last - prev); df["Weight"] = df.Value / df.Value.sum() if df.Value.sum() else 0.0
    return df


def optimise(lookback: int | None = None) -> dict:
    """Current suggested allocation from the most recent `lookback` sessions (historical mean,
    Ledoit-Wolf covariance, long-only, per-asset cap). A forward-looking decision input, not a result."""
    c = cfg(); lookback = lookback or c["backtest"]["lookback_sessions"]
    r = equity_returns().tail(lookback).dropna()
    cov, shrink = FN.ledoit_wolf(r); cov *= TD; mu = r.mean() * TD; rf, cap = c["risk_free_rate_annual"], c["max_weight"]
    w_ms, w_mv = FN.max_sharpe(mu, cov, rf, cap), FN.min_variance(cov, cap)
    ew = pd.Series(1 / len(mu), index=mu.index)
    return {"mu": mu, "cov": cov, "shrinkage": shrink, "rf": rf, "cap": cap, "window": (r.index.min(), r.index.max()),
            "max_sharpe": w_ms, "min_variance": w_mv, "equal_weight": ew,
            "perf": {k: FN.perf(w, mu, cov, rf) for k, w in [("Max Sharpe", w_ms), ("Min variance", w_mv), ("Equal weight", ew)]},
            "frontier": FN.efficient_frontier(mu, cov, cap), "monte_carlo": FN.monte_carlo(mu, cov, rf)}


@lru_cache(maxsize=1)
def backtest_validation() -> dict:
    """Rebalanced strategies over the VALIDATION window only (2024-01-01..2026-05-08)."""
    c = cfg(); b = c["backtest"]; r = equity_returns(); rf = c["risk_free_rate_annual"]
    start, end = config.TRAIN_TARGET_END + pd.Timedelta(days=1), config.VALIDATION_TARGET_END
    bench = risk.returns_wide()[market.BENCHMARK]
    series, weights, stats = {}, {}, []
    for key, label in [("max_sharpe", "Max Sharpe (optimised)"), ("min_variance", "Minimum variance"), ("equal_weight", "Equal weight")]:
        ret, w, to = FN.backtest(r, start, end, key, rf, c["max_weight"], b["lookback_sessions"], b["rebalance_every_sessions"], c["transaction_cost_bps_one_way"])
        series[label], weights[label] = ret, w
        stats.append({"Strategy": label, **FN.summary(ret, rf, bench), "Turnover (one-way)": to, "Rebalances": len(w)})
    nb = bench[(bench.index >= start) & (bench.index <= end)].dropna()
    series["NIFTY 50 price index"] = nb
    stats.append({"Strategy": "NIFTY 50 price index", **FN.summary(nb, rf, bench), "Turnover (one-way)": 0.0, "Rebalances": 0})
    return {"series": series, "weights": weights, "stats": pd.DataFrame(stats).set_index("Strategy"), "start": start, "end": end,
            "initial": b["initial_value_inr"]}


# ---------------- recommendations ----------------
def recommendations(holdings: pd.DataFrame, use_unvalidated_forecast: bool = False, target: str = "min_variance") -> dict:
    """BUY/HOLD/SELL per stock plus an optional rebalancing plan toward `target`
    ('min_variance' needs no return estimate; 'max_sharpe' uses historical means)."""
    c = dict(cfg()); reg = registry()
    if use_unvalidated_forecast:
        c["require_validated_edge"] = False
    try:
        fc = forecasts(); fmap = fc["forecast_log_return"].to_dict(); as_of = fc["as_of"].max()
    except InferenceUnavailable:
        fmap, as_of = {}, market.load_panel().Date.max()
    vol = equity_returns().tail(c["volatility_window_sessions"]).std()
    val = value_holdings(holdings)
    dec = R.decide(tickers(), fmap, vol, sentiment_signal(as_of), val["Weight"], c, reg.validated_edge)
    target_w = optimise()[target]
    return {"decisions": dec, "table": pd.DataFrame([d.row() for d in dec]).set_index("ticker"), "summary": R.portfolio_action(dec),
            "rebalance": R.rebalance(val["Weight"], target_w, c["rebalance_band"]), "target": target, "model": reg.selected,
            "validated_edge": reg.validated_edge, "as_of": as_of, "config": c}

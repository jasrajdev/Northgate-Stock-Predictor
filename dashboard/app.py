"""Northgate Stock Predictor: investor dashboard.

Run from the repository root:
    .venv/bin/streamlit run dashboard/app.py

Reads saved data, persisted models and saved results through `northgate.backend.api`.
It never trains a model, downloads data or opens the held-out test partition.
"""
from __future__ import annotations
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")  # PyTorch + scikit-learn OpenMP clash on macOS
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import theme as T
from northgate import finance as FN
from northgate.backend import api

st.set_page_config(page_title="Northgate · Investor Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown(T.CSS, unsafe_allow_html=True)

PANELS = ["Overview", "Price & Prediction", "Recommendations", "Portfolio Analytics", "Risk Dashboard", "Sentiment", "Model Comparison"]
DISCLAIMER = "Educational research tool. Not financial advice. No forecasting model has beaten a simple no-change forecast on validation data."


# ---------------- cached backend ----------------
@st.cache_data(show_spinner=False)
def c_overview(): return api.overview()
@st.cache_data(show_spinner=False)
def c_history(t): return api.stock_history(t)
@st.cache_data(show_spinner=False)
def c_risk(s, e): return api.risk_summary(s, e)
@st.cache_data(show_spinner=False)
def c_corr(s, e): return api.correlation(s, e)
@st.cache_data(show_spinner=False)
def c_dd(t): return api.drawdown_series(t)
@st.cache_data(show_spinner=False)
def c_rv(t): return api.rolling_volatility(t)
@st.cache_data(show_spinner=False)
def c_exp(): return api.experiment()
@st.cache_resource(show_spinner="Loading models…")
def c_registry(): return api.registry()
@st.cache_data(show_spinner=False)
def c_forecasts(model): return api.forecasts(model)
@st.cache_data(show_spinner=False)
def c_all_fc(): return api.all_forecasts()
@st.cache_data(show_spinner=False)
def c_valpath(model, t): return api.validation_path(model, t)
@st.cache_data(show_spinner=False)
def c_band(model, t): return api.error_band(model, t)
@st.cache_data(show_spinner="Optimising…")
def c_opt(): return api.optimise()
@st.cache_data(show_spinner="Running validation backtest…")
def c_bt(): return api.backtest_validation()
@st.cache_data(show_spinner=False)
def c_rec(h, unval, target): return api.recommendations(h, unval, target)
@st.cache_data(show_spinner=False)
def c_ctx(): return api.market_context()
@st.cache_data(show_spinner=False)
def c_sent(): return api.sentiment()
@st.cache_data(show_spinner=False)
def c_localval(): return api.local_classical_validation()


# ---------------- helpers ----------------
def header(title, lede, tags):
    st.markdown('<div class="ng-kicker">Northgate Stock Predictor</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown("".join(T.tag(t, off) for t, off in tags), unsafe_allow_html=True)
    if lede:
        st.markdown(f'<p class="ng-lede">{lede}</p>', unsafe_allow_html=True)


def note(label, text):
    st.markdown(f'<div class="ng-note"><b>{label}</b><br>{text}</div>', unsafe_allow_html=True)


def pct(x, d=2, sign=False):
    return "n/a" if x is None or pd.isna(x) else f"{x * 100:{'+' if sign else ''}.{d}f}%"


def inr(x, d=0):
    return "n/a" if x is None or pd.isna(x) else f"₹{x:,.{d}f}"


def chart(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def short(t):
    return t.replace(".NS", "")


def model_status(m) -> tuple[str, str]:
    """Readable status and explanation for a registry entry (presentation only; the registry is unchanged)."""
    if m.loaded:
        return "Ready", ("Fitted on the training period" if m.family == "Classical" else "Checkpoint loaded")
    d = m.detail or ""
    if "feature order differs" in d:
        import re
        n = re.search(r"\((\d+) vs (\d+)\)", d)
        sizes = f"expects {n.group(1)} inputs, pipeline supplies {n.group(2)}" if n else "expects different inputs"
        return "Unavailable", f"Incompatible checkpoint: {sizes}"
    if "not present" in d:
        return "Unavailable", "Checkpoint not installed"
    if m.family == "Classical":
        return "Unavailable", "Not fitted yet (scripts/persist_classical_models.py)"
    return "Unavailable", "Checkpoint failed to load; see technical details"


def holdings() -> pd.DataFrame:
    if "holdings" not in st.session_state:
        st.session_state.holdings = api.example_holdings()
    return st.session_state.holdings


# =================== 1. OVERVIEW (landing) ===================
def overview():
    ov, reg, names = c_overview(), c_registry(), api.names()
    h = holdings(); val = api.value_holdings(h)
    rec = c_rec(h, False, "min_variance")
    try:
        fc = c_forecasts(reg.selected)
    except Exception:
        fc = None
    tbl = ov["table"]
    header("Portfolio overview", None, [(f"Data as of {ov['last_date']:%d %b %Y}", False), ("Example portfolio · editable", False)])

    total, day = val.Value.sum(), val["Day change"].sum()
    ctx = c_ctx(); vix_txt, vix_sub = "n/a", "not downloaded"
    if ctx.get("available"):
        v = ctx["context"]; v = v[(v.Ticker == "^INDIAVIX") & (v.Date <= ov["last_date"])].dropna(subset=["Close"])
        if len(v):
            pctile = (v.Close.tail(756) <= v.Close.iloc[-1]).mean()
            vix_txt, vix_sub = f"{v.Close.iloc[-1]:.2f}", f"{pctile:.0%} percentile of 3 years"
    nifty = tbl.loc["^NSEI"]
    decision = "No action" if rec["summary"].startswith("No action") else rec["summary"].split(":")[0]
    st.markdown(T.figures([
        ("Portfolio value", inr(total), f"{len(val)} holdings"),
        ("Last session", f"{'+' if day >= 0 else '−'}{inr(abs(day))}", pct(day / (total - day), 2, True)),
        ("NIFTY 50", f"{nifty.Close:,.0f}", f"{pct(nifty['1 session'], 2, True)} session · {pct(nifty['1 year (252)'], 1, True)} 1y"),
        ("India VIX", vix_txt, vix_sub),
        ("Decision today", decision, "details under Recommendations"),
    ]), unsafe_allow_html=True)

    with st.container():
        st.subheader("Watchlist and decisions")
        rows = []
        for t in api.tickers():
            r = tbl.loc[t]; d = rec["table"].loc[t]
            rows.append({"Stock": short(t), "Company": names[t], "Last close": r.Close, "Session": r["1 session"] * 100,
                         "1 year": r["1 year (252)"] * 100, "3-month trend": r["3 months"],
                         "Forecast": (fc.loc[t, "forecast_return"] * 100) if fc is not None else np.nan,
                         "Decision": d.action, "Weight": val.loc[t, "Weight"] * 100})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=388, column_config={
            "Stock": st.column_config.TextColumn(width=112),
            "Company": st.column_config.TextColumn(width=190),
            "Last close": st.column_config.NumberColumn(format="₹%.2f", width=88),
            "Session": st.column_config.NumberColumn(format="%+.2f%%", width=76),
            "1 year": st.column_config.NumberColumn(format="%+.1f%%", width=72),
            "3-month trend": st.column_config.LineChartColumn("3-mo trend", width=92, help="Adjusted close, last 63 sessions"),
            "Forecast": st.column_config.NumberColumn("Forecast", format="%+.2f%%", width=80,
                                                      help=f"Next-session forecast from the {reg.selected} model. Unvalidated: it did not beat the no-change forecast."),
            "Decision": st.column_config.TextColumn(width=76),
            "Weight": st.column_config.NumberColumn(format="%.1f%%", width=70)})
    left, right = st.columns([2, 3], gap="large")
    with left:
        st.subheader("Decision")
        note("Why every decision is HOLD" if decision == "No action" else "Decisions",
             f"{rec['summary']}. The {reg.selected} forecast is displayed but carries no weight in the decision, because no model beat "
             "a simple no-change forecast on validation data. Holding is a valid outcome; the system never forces a trade.")
        st.subheader("Risk snapshot")
        pr = (api.equity_returns().tail(252)[val.index] * val.Weight).sum(axis=1)
        st.markdown(T.figures([
            ("Volatility", pct(FN.annualise_vol(pr), 1), "annualised, 1 year"),
            ("1-day VaR 95%", inr(-FN.var_historical(pr) * total), "historical"),
            ("Beta", f"{FN.beta(pr, api.risk.returns_wide()['^NSEI']):.2f}", "vs NIFTY 50"),
        ], compact=True), unsafe_allow_html=True)
        st.caption("Today's holdings applied to the past year of returns. Details on the Risk Dashboard.")
    with right:
        st.subheader("Allocation")
        w = val["Weight"].sort_values()
        fig = go.Figure(go.Bar(x=w.values * 100, y=[short(t) for t in w.index], orientation="h", width=0.6,
                               marker=dict(color=T.BLUE, line=dict(color=T.PAPER, width=2)),
                               hovertemplate="%{y}: %{x:.1f}%<extra></extra>", name="Current"))
        tgt = c_opt()["min_variance"].reindex(w.index)
        fig.add_trace(go.Scatter(x=tgt.values * 100, y=[short(t) for t in w.index], mode="markers", name="Min-variance target",
                                 marker=dict(symbol="line-ns", size=14, line=dict(width=2.5, color=T.ORANGE)),
                                 hovertemplate="%{y} target: %{x:.1f}%<extra></extra>"))
        T.style(fig, 360).update_layout(hovermode="closest")
        fig.update_xaxes(ticksuffix="%", showgrid=True, gridcolor=T.GRID)
        chart(fig)
        st.caption("Bars: current weights. Orange ticks: minimum-variance target with a 30% cap. The rebalancing plan is under Recommendations.")

    st.subheader("Market")
    sectors = {"^NSEBANK": "NIFTY Bank", "^CNXIT": "NIFTY IT", "^CNXPHARMA": "NIFTY Pharma", "^CNXFMCG": "NIFTY FMCG",
               "^CNXAUTO": "NIFTY Auto", "^CNXENERGY": "NIFTY Energy", "^CNXMETAL": "NIFTY Metal"}
    if ctx.get("available"):
        c = ctx["context"]; c = c[c.Date <= ov["last_date"]]
        rows = []
        for k, lab in sectors.items():
            s = c[c.Ticker == k].dropna(subset=["Close"]).sort_values("Date").Close
            if len(s) > 253:
                rows.append({"Index": lab, "Level": s.iloc[-1], "Session": (s.iloc[-1] / s.iloc[-2] - 1) * 100,
                             "1 month": (s.iloc[-1] / s.iloc[-22] - 1) * 100, "1 year": (s.iloc[-1] / s.iloc[-253] - 1) * 100})
        m = pd.DataFrame(rows).sort_values("1 year")
        fig = go.Figure(go.Bar(x=m["1 year"], y=m.Index, orientation="h", width=0.6, marker=dict(color=T.NEUTRAL, line=dict(color=T.PAPER, width=2)),
                               text=[f"{v:+.1f}%" for v in m["1 year"]], textposition="outside", textfont=dict(family="Menlo, monospace", size=11),
                               hovertemplate="%{y}: %{x:+.1f}% over 1 year<extra></extra>"))
        fig.add_vline(x=nifty["1 year (252)"] * 100, line=dict(color=T.INK, width=1, dash="dash"))
        fig.add_annotation(x=nifty["1 year (252)"] * 100, y=1.05, yref="paper", text=f"NIFTY 50 {nifty['1 year (252)'] * 100:+.1f}%",
                           showarrow=False, font=dict(family="Menlo, monospace", size=11))
        fig.update_traces(cliponaxis=False)
        T.style(fig, 300, legend=False).update_layout(hovermode="closest", margin=dict(l=8, r=48, t=34, b=8))
        span = max(abs(m["1 year"]).max(), 5) * 1.25
        fig.update_xaxes(ticksuffix="%", showgrid=True, gridcolor=T.GRID, range=[-span, span])
        a, b = st.columns([1, 1], gap="large")
        with a:
            chart(fig)
        with b:
            st.dataframe(m.drop(columns=["Level"]).set_index("Index").sort_values("1 year", ascending=False), width="stretch", column_config={
                "Session": st.column_config.NumberColumn(format="%+.2f%%"),
                "1 month": st.column_config.NumberColumn(format="%+.1f%%"), "1 year": st.column_config.NumberColumn(format="%+.1f%%")})
        st.caption("Sector indices and India VIX from Yahoo Finance, cut at the last session of the stock data. News-based market mood is on the Sentiment page.")
    else:
        st.caption("Sector and volatility data not downloaded. Run scripts/download_market_context.py.")

    with st.expander("Edit holdings (kept in this browser session only)"):
        ed = st.data_editor(holdings(), width="stretch", column_config={"Shares": st.column_config.NumberColumn(min_value=0, step=1)})
        if st.button("Apply holdings"):
            st.session_state.holdings = ed.astype({"Shares": int}); st.rerun()
        st.caption("Default: an illustrative equal-rupee portfolio (₹1,00,000 per stock at the latest close). It is not a performance record.")


# =================== 2. PRICE & PREDICTION ===================
def price_prediction():
    ov, reg, names = c_overview(), c_registry(), api.names()
    header("Price & prediction", None, [(f"Model: {reg.selected}", False), ("Forecast not validated", True)])
    a, b = st.columns([2, 3])
    t = a.selectbox("Stock", api.tickers(), format_func=lambda x: f"{short(x)} · {names[x]}")
    span = b.radio("Period", ["6 months", "1 year", "3 years", "All"], index=1, horizontal=True)
    h = c_history(t); fc = c_forecasts(reg.selected).loc[t]
    lo, hi = c_band(reg.selected, t)
    last = h.iloc[-1]
    band = [fc.price * np.exp(fc.forecast_log_return + q) for q in (lo, hi)]
    st.markdown(T.figures([
        ("Last close", inr(last.Close, 2), f"{last.Date:%d %b %Y}"),
        ("Next-session forecast", inr(fc.forecast_price, 2), f"{pct(fc.forecast_return, 2, True)} ({reg.selected})"),
        ("80% error range", f"{inr(band[0])} – {inr(band[1])}", "from validation errors"),
        ("RSI (14)", f"{last.rsi_14:.0f}" if pd.notna(last.get('rsi_14')) else "n/a", "momentum, 0–100"),
        ("Volatility (20d)", pct(last.volatility_20d * np.sqrt(252), 1) if pd.notna(last.get('volatility_20d')) else "n/a", "annualised"),
    ]), unsafe_allow_html=True)

    months = {"6 months": 6, "1 year": 12, "3 years": 36}.get(span)
    hv = h[h.Date >= h.Date.max() - pd.DateOffset(months=months)] if months else h
    vp = c_valpath(reg.selected, t); vp = vp[vp.target_date_t1 >= hv.Date.min()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hv.Date, y=hv["Adj Close"], name="Adjusted close", mode="lines", line=dict(color=T.BLUE, width=2), hovertemplate="₹%{y:,.2f}"))
    if "sma_50" in hv:
        fig.add_trace(go.Scatter(x=hv.Date, y=hv.sma_50, name="50-session average", mode="lines", line=dict(color=T.NEUTRAL, width=1.2), hovertemplate="₹%{y:,.2f}"))
    if len(vp):
        fig.add_trace(go.Scatter(x=vp.target_date_t1, y=vp.pred_price, name=f"{reg.selected} one-step forecast (validation)", mode="lines",
                                 line=dict(color=T.ORANGE, width=1.2, dash="dot"), hovertemplate="₹%{y:,.2f}"))
    nxt = fc.as_of + pd.offsets.BDay(1)
    fig.add_trace(go.Scatter(x=[nxt, nxt], y=band, mode="lines", line=dict(color=T.ORANGE, width=7), opacity=0.35, name="80% error range", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[fc.as_of, nxt], y=[fc.price, fc.forecast_price], mode="lines+markers", name="Next-session forecast",
                             line=dict(color=T.ORANGE, width=2), marker=dict(size=[0, 10], color=T.ORANGE, line=dict(color=T.PAPER, width=2)),
                             hovertemplate="₹%{y:,.2f}"))
    for d, lab in ((ov["train_end"], "training ends"), (ov["validation_end"], "validation ends")):
        if hv.Date.min() <= d <= hv.Date.max():
            fig.add_vline(x=d, line=dict(color=T.NEUTRAL, width=1, dash="dot"))
            fig.add_annotation(x=d, y=1, yref="paper", text=lab, showarrow=False, xanchor="right", yanchor="top",
                               font=dict(family="Menlo, monospace", size=10, color=T.MUTED), xshift=-4)
    chart(T.style(fig, 430, "INR"))
    st.caption("Dotted orange: the model's one-session-ahead forecast on validation dates. Forecasts are not drawn over the held-out "
               "test window (after 8 May 2026), which has not been evaluated. Error range: 10th–90th percentile of this model's "
               "validation errors for this stock.")

    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.subheader("Every available model, next session")
        af = c_all_fc()
        if len(af):
            row = af.loc[t] * 100; status = {m.name: m for m in reg.models}
            d = pd.DataFrame({"Model": row.index, "Family": [status[m].family for m in row.index], "Forecast return": row.values,
                              "Validation MAE vs naive": [(status[m].validation_mae / reg.naive_mae - 1) * 100 for m in row.index]})
            st.dataframe(d, hide_index=True, width="stretch", column_config={
                "Forecast return": st.column_config.NumberColumn(format="%+.3f%%"),
                "Validation MAE vs naive": st.column_config.NumberColumn(format="%+.2f%%", help="Experiment 01; positive = worse than no-change")})
            missing = [m for m in reg.models if not m.loaded]
            if missing:
                why = "checkpoints incompatible with the current feature pipeline" if all("feature order" in (m.detail or "") for m in missing) else "not available"
                st.caption("Not shown: " + ", ".join(m.name for m in missing) + f" ({why}; see Model Comparison). "
                           "The available models are shown side by side, not averaged.")
    with c2:
        st.subheader("RSI (14)")
        fig = go.Figure(go.Scatter(x=hv.Date, y=hv.rsi_14, mode="lines", line=dict(color=T.BLUE, width=1.4), hovertemplate="%{y:.0f}", name="RSI"))
        for lvl in (30, 70):
            fig.add_hline(y=lvl, line=dict(color=T.NEUTRAL, width=1, dash="dot"))
        chart(T.style(fig, 250, legend=False).update_yaxes(range=[0, 100]))


# =================== 3. RECOMMENDATIONS ===================
def recommendations():
    header("Recommendations", "Rule-based decisions with every input shown. Thresholds and weights live in config/recommendation.json.",
           [("Transparent rules", False), ("No forced trades", False)])
    a, b = st.columns(2)
    unval = a.toggle("Include the unvalidated forecast (experimental)", value=False,
                     help="Shows what the rules would say if the forecast were trusted. It has not beaten a no-change forecast.")
    target = b.radio("Rebalancing target", ["min_variance", "max_sharpe"], horizontal=True,
                     format_func=lambda x: {"min_variance": "Minimum variance", "max_sharpe": "Max Sharpe (historical means)"}[x])
    rec = c_rec(holdings(), unval, target); c = rec["config"]
    note("Portfolio decision", f"<span style='font-size:1.1rem'>{rec['summary']}</span><br>As of the close of {rec['as_of']:%d %b %Y}. "
         f"Forecast model: {rec['model']}" + (" (experimental: forecast included)." if unval else " (forecast weight set to zero: no validated edge)."))
    st.subheader("Per-stock decision")
    t = rec["table"]
    sent = [("no data" if pd.isna(v) else f"{v:+.2f}") for v in t.sentiment_signal]
    show = pd.DataFrame({"Stock": [short(x) for x in t.index], "Decision": t.action, "Composite": t.composite, "Forecast": t.forecast_return * 100,
                         "Forecast signal": t.forecast_signal, "Sentiment": sent, "Risk signal": t.risk_signal, "Weight": t.weight * 100})
    st.dataframe(show, hide_index=True, width="stretch", height=388, column_config={
        "Stock": st.column_config.TextColumn(width="small"), "Decision": st.column_config.TextColumn(width="small"),
        "Composite": st.column_config.NumberColumn(format="%+.2f", width="small", help="Weighted score; see the rule below"),
        "Forecast": st.column_config.NumberColumn(format="%+.2f%%", width="small", help="Next-session forecast return"),
        "Forecast signal": st.column_config.NumberColumn(format="%+.2f", width="small", help="Forecast divided by recent daily volatility"),
        "Sentiment": st.column_config.TextColumn(width="small", help="Recent headline polarity; 'no data' when no headlines are available"),
        "Risk signal": st.column_config.NumberColumn(format="%+.2f", width="small", help="Volatility relative to the other stocks (positive = riskier)"),
        "Weight": st.column_config.NumberColumn(format="%.1f%%", width="small")})
    st.subheader("Why each decision was made")
    st.markdown(T.reasons([(short(x), r.action, {"BUY": T.GREEN, "SELL": T.ORANGE, "REDUCE": T.ORANGE}.get(r.action, T.MUTED),
                            r.reasons[0].upper() + r.reasons[1:] if r.reasons else "") for x, r in t.iterrows()]), unsafe_allow_html=True)
    w = c["signal_weights"]
    st.markdown(f"**Rule.** composite = {w['forecast']} × forecast signal + {w['sentiment']} × sentiment − {w['risk']} × max(risk, 0). "
                f"BUY at ≥ {c['buy_threshold']} with a positive forecast or sentiment contribution and weight below {c['max_weight']:.0%}; "
                f"SELL at ≤ {c['sell_threshold']} with a negative contribution and an existing holding; REDUCE only above "
                f"{c['max_weight'] + c['rebalance_band']:.0%} weight; otherwise HOLD. Forecasts smaller than the round-trip cost "
                f"({2 * c['transaction_cost_bps_one_way']} bps) are ignored. Risk can lower conviction but cannot trigger a sale, and no stock "
                "is sold because another looks better.")

    st.subheader("Rebalancing plan")
    rb = rec["rebalance"].copy(); total = api.value_holdings(holdings()).Value.sum()
    rb["Trade value"] = rb.drift * total
    cost = rb.loc[rb.action != "within band", "Trade value"].abs().sum() * c["transaction_cost_bps_one_way"] / 1e4
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[short(x) for x in rb.index], y=rb.current * 100, name="Current", marker=dict(color=T.BLUE, line=dict(color=T.PAPER, width=2))))
    fig.add_trace(go.Bar(x=[short(x) for x in rb.index], y=rb.target * 100, name="Target", marker=dict(color=T.ORANGE, line=dict(color=T.PAPER, width=2))))
    chart(T.style(fig, 300, "weight %").update_layout(barmode="group", bargap=0.35))
    st.dataframe(pd.DataFrame({"Stock": [short(x) for x in rb.index], "Current": rb.current * 100, "Target": rb.target * 100,
                               "Drift": rb.drift * 100, "Action": rb.action, "Trade value": rb["Trade value"]}), hide_index=True, width="stretch",
                 column_config={"Current": st.column_config.NumberColumn(format="%.1f%%"), "Target": st.column_config.NumberColumn(format="%.1f%%"),
                                "Drift": st.column_config.NumberColumn(format="%+.1f%%"), "Trade value": st.column_config.NumberColumn(format="₹%,.0f")})
    st.caption(f"Trades only where drift exceeds ±{c['rebalance_band']:.0%}. Estimated cost: {inr(cost)} at {c['transaction_cost_bps_one_way']} bps "
               "per side (assumption). This is a portfolio-construction suggestion, separate from the per-stock decisions; the "
               "minimum-variance target uses only risk, not return forecasts.")


# =================== 4. PORTFOLIO ANALYTICS ===================
def portfolio():
    o, bt = c_opt(), c_bt()
    header("Portfolio analytics", "Long-only mean-variance optimisation with Ledoit-Wolf covariance and a 30% per-stock cap.",
           [("Implemented", False), ("Backtest on validation window only", False)])
    ms = o["perf"]["Max Sharpe"]
    st.markdown(T.figures([
        ("Estimation window", f"{o['window'][0]:%b %Y} – {o['window'][1]:%b %Y}", "504 sessions"),
        ("Covariance shrinkage", f"{o['shrinkage']:.2f}", "Ledoit-Wolf intensity"),
        ("Max-Sharpe (in-sample)", f"{ms[2]:.2f}", f"return {pct(ms[0], 1)}, vol {pct(ms[1], 1)}"),
        ("Min-variance volatility", pct(o['perf']['Min variance'][1], 1), "annualised"),
        ("Risk-free rate", pct(o["rf"], 1), "assumption"),
    ]), unsafe_allow_html=True)
    st.subheader("Efficient frontier and 20,000 random portfolios")
    mc, fr = o["monte_carlo"], o["frontier"]
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=mc.volatility * 100, y=mc["return"] * 100, mode="markers", name="Random portfolios (uncapped)",
                               marker=dict(size=3, color=T.NEUTRAL, opacity=0.25), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=fr.volatility * 100, y=fr["return"] * 100, mode="lines", name="Efficient frontier (30% cap)",
                             line=dict(color=T.BLUE, width=2.5), hovertemplate="vol %{x:.1f}%, return %{y:.1f}%<extra></extra>"))
    for k, col, sym in (("Max Sharpe", T.ORANGE, "diamond"), ("Min variance", T.GREEN, "circle"), ("Equal weight", T.VIOLET, "square")):
        r_, v_, s_ = o["perf"][k]
        fig.add_trace(go.Scatter(x=[v_ * 100], y=[r_ * 100], mode="markers+text", name=k, text=[k], textposition="top center",
                                 textfont=dict(family="Menlo, monospace", size=11), marker=dict(size=13, color=col, symbol=sym, line=dict(color=T.PAPER, width=2)),
                                 hovertemplate=f"{k}: vol %{{x:.1f}}%, return %{{y:.1f}}%, Sharpe {s_:.2f}<extra></extra>"))
    T.style(fig, 440).update_layout(hovermode="closest")
    fig.update_xaxes(title=dict(text="annualised volatility", font=dict(size=12, color=T.MUTED)), ticksuffix="%", showgrid=True, gridcolor=T.GRID)
    fig.update_yaxes(ticksuffix="%", title=dict(text="expected annual return (historical mean)"))
    chart(fig)
    st.caption("Expected returns are historical means over the estimation window: noisy, and a description of the past rather than a forecast. "
               "The Monte Carlo cloud cross-checks the optimiser; it is uncapped, so it can extend beyond the capped frontier.")
    st.subheader("Weights")
    wt = pd.DataFrame({k: o[s] * 100 for k, s in (("Max Sharpe", "max_sharpe"), ("Min variance", "min_variance"), ("Equal weight", "equal_weight"))})
    wt.index = [short(x) for x in wt.index]
    st.dataframe(wt, width="stretch", column_config={k: st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=30) for k in wt.columns})

    st.subheader(f"Validation backtest, {bt['start']:%d %b %Y} – {bt['end']:%d %b %Y}")
    fig = go.Figure()
    for (k, s), col in zip(bt["series"].items(), [T.ORANGE, T.GREEN, T.VIOLET, T.INK]):
        v = bt["initial"] * (1 + s.fillna(0)).cumprod()
        fig.add_trace(go.Scatter(x=v.index, y=v.values, name=k, mode="lines", hovertemplate="₹%{y:,.0f}",
                                 line=dict(color=col, width=2 if "Max" in k else 1.4, dash="dash" if "NIFTY" in k else "solid")))
    chart(T.style(fig, 380, "portfolio value, INR"))
    stats = bt["stats"].copy()
    fmt = {c: st.column_config.NumberColumn(format="%.2f") for c in ("Sharpe", "Sortino", "Calmar", "Beta", "Turnover (one-way)")}
    for c in ("Total return", "CAGR", "Volatility", "Max drawdown", "VaR 95% (1-day)"):
        stats[c] = stats[c] * 100; fmt[c] = st.column_config.NumberColumn(format="%.2f%%")
    st.dataframe(stats, width="stretch", column_config=fmt)
    note("How to read the backtest", "Weights at each quarterly rebalance use only the previous 504 sessions. Costs of 10 bps per side are charged "
         "on turnover. The benchmark is the NIFTY 50 price index, which excludes dividends while the portfolios include them, so the comparison "
         "favours the portfolios by roughly the index dividend yield. The held-out test window is not used. One period, one market: "
         "this is not evidence of future outperformance.")


# =================== 5. RISK ===================
def risk_dashboard():
    ov, names = c_overview(), api.names()
    header("Risk dashboard", "Historical measurements of past daily returns.", [("Implemented", False), ("Historical only", False)])
    val = api.value_holdings(holdings()); w = val.Weight
    pr = (api.equity_returns().tail(252)[w.index] * w).sum(axis=1)
    bench = api.risk.returns_wide()["^NSEI"]
    st.markdown(T.figures([
        ("Portfolio volatility", pct(FN.annualise_vol(pr), 1), "last 252 sessions"),
        ("1-day VaR 95%", inr(-FN.var_historical(pr) * val.Value.sum()), pct(FN.var_historical(pr), 2)),
        ("Max drawdown", pct(FN.max_drawdown(pr), 1), "last 252 sessions"),
        ("Beta vs NIFTY 50", f"{FN.beta(pr, bench):.2f}", "last 252 sessions"),
        ("Sortino", f"{FN.sortino(pr, api.cfg()['risk_free_rate_annual']):.2f}", "risk-free 6.5% (assumption)"),
    ]), unsafe_allow_html=True)
    st.caption("Portfolio figures apply today's holdings to the last year of returns: a what-if on past data, not a track record.")
    periods = {"Full history": (None, None), "Training (to Dec 2023)": (None, ov["train_end"]),
               "Validation (Jan 2024 – May 2026)": (ov["train_end"] + pd.Timedelta(days=1), ov["validation_end"])}
    s, e = periods[st.radio("Period", list(periods), horizontal=True)]
    rs = c_risk(s, e).copy()
    for c in ("Annualised return", "Annualised volatility", "Maximum drawdown", "1-day VaR 95% (historical)", "Worst day"):
        rs[c] = rs[c] * 100
    if "^NSEI" in rs.index:
        rs.loc["^NSEI", "Beta vs NIFTY 50"] = 1.0  # the benchmark's beta against itself is 1 by definition
    rs.index = pd.Index(["NIFTY 50" if x == "^NSEI" else short(x) for x in rs.index], name="Stock")
    labels = {"Annualised return": ("Return p.a.", "Annualised (compound) return of the adjusted close"),
              "Annualised volatility": ("Volatility p.a.", "Standard deviation of daily returns × √252"),
              "Maximum drawdown": ("Max drawdown", "Largest fall from a previous peak"),
              "1-day VaR 95% (historical)": ("1-day VaR 95%", "5th percentile of daily returns (historical)"),
              "Worst day": ("Worst day", "Lowest single-day return"), "Beta vs NIFTY 50": ("Beta", "Sensitivity to NIFTY 50 daily returns")}
    fmt = {k: st.column_config.NumberColumn(lab, help=h, format="%.2f" if k.startswith("Beta") else "%.1f%%", width="small") for k, (lab, h) in labels.items()}
    fmt["Sessions"] = st.column_config.NumberColumn(width="small")
    st.dataframe(rs, width="stretch", height=35 * (len(rs) + 1) + 3, column_config=fmt)
    t = st.selectbox("Stock for the charts", api.tickers(True), format_func=lambda x: f"{short(x)} · {names[x]}")
    a, b = st.columns(2)
    with a:
        st.subheader("Drawdown from peak")
        dd = c_dd(t)
        fig = go.Figure(go.Scatter(x=dd.index, y=dd.values * 100, mode="lines", line=dict(color=T.ORANGE, width=1.4), fill="tozeroy",
                                   fillcolor="rgba(194,87,26,0.12)", hovertemplate="%{y:.1f}%"))
        chart(T.style(fig, 280, legend=False).update_yaxes(ticksuffix="%"))
    with b:
        st.subheader("Rolling 20-session volatility")
        rv = c_rv(t).dropna()
        fig = go.Figure(go.Scatter(x=rv.index, y=rv.values * 100, mode="lines", line=dict(color=T.BLUE, width=1.4), hovertemplate="%{y:.1f}%"))
        chart(T.style(fig, 280, legend=False).update_yaxes(ticksuffix="%"))
    st.subheader("Correlation of daily returns")
    cm = c_corr(s, e); lab = [short(x) for x in cm.columns]
    fig = go.Figure(go.Heatmap(z=cm.values, x=lab, y=lab, zmin=0, zmax=1, colorscale=T.SEQUENTIAL, xgap=2, ygap=2,
                               text=[[f"{v:.2f}" for v in row] for row in cm.values], texttemplate="%{text}",
                               textfont=dict(family="Menlo, monospace", size=10), colorbar=dict(thickness=10, len=0.8),
                               hovertemplate="%{y} / %{x}: %{z:.2f}<extra></extra>"))
    T.style(fig, 440, legend=False).update_layout(hovermode="closest")
    fig.update_xaxes(showline=False, ticks=""); fig.update_yaxes(autorange="reversed", showgrid=False, showline=False, ticks="")
    chart(fig)


# =================== 6. SENTIMENT ===================
def sentiment():
    s, ov, names = c_sent(), c_overview(), api.names()
    if not s["available"]:
        header("Sentiment", "Daily sentiment from timestamped financial headlines, scored with FinBERT and VADER.",
               [("No headline data", True), ("Pipeline implemented", False)])
        st.markdown(T.figures([("Headlines stored", "0", "none fetched on this machine"), ("Market mood", "n/a", "needs headline data"),
                               ("Used in decisions", "No", "sentiment weight is zero without data")]), unsafe_allow_html=True)
        note("No sentiment is shown", "There is currently no headline data, so this page shows no scores and the recommendation engine gives "
             "sentiment zero weight. Nothing here is estimated or filled in. The free GDELT news API rate-limited this machine and returned "
             "no articles when the fetch was attempted.")
        st.subheader("Pipeline status")
        st.markdown(T.steps([
            ("Step 1", "Fetch headlines", "Titles, links and first-seen times for each company from GDELT (no article text stored).", "Not yet run successfully", False),
            ("Step 2", "Map to trading sessions", "Headlines after the 15:30 IST close or on non-trading days count for the next NSE session.", "Implemented and tested", True),
            ("Step 3", "Score sentiment", "VADER compound score for every headline; FinBERT positive/negative/neutral probabilities when installed.", "Implemented", True),
            ("Step 4", "Daily features", "Per stock and session: mean score, headline count, 3-session momentum and a news-volume spike flag.", "Implemented", True),
        ]), unsafe_allow_html=True)
        st.subheader("To populate this page")
        st.markdown('<div class="ng-code">python scripts/fetch_news_gdelt.py\npython scripts/score_news_sentiment.py</div>', unsafe_allow_html=True)
        st.caption("GDELT's free API covers only a recent rolling window, so even when it works it cannot supply 2016–2025 history for model "
                   "training; the with/without-sentiment comparison required by the brief therefore remains open.")
        return
    items, daily = s["items"], s["daily"]
    src = {"finbert_polarity": "FinBERT", "vader_compound": "VADER"}.get(s["score_source"], s["score_source"])
    header("Sentiment", f"Recent headlines from GDELT scored with {src}. Each headline counts from the first NSE session after it was "
           "first seen; items after 15:30 IST roll to the next session.", [("Recent window only", False), (f"Scorer: {src}", False)])
    used = daily[daily.session <= ov["last_date"]]
    mood = used.groupby("ticker").apply(lambda g: np.average(g.score.tail(5), weights=g.articles.tail(5)), include_groups=False)
    mkt = mood.drop(index="^NSEI", errors="ignore").mean() if len(mood) else np.nan
    label = "n/a" if pd.isna(mkt) else ("Positive" if mkt > 0.1 else "Negative" if mkt < -0.1 else "Neutral")
    st.markdown(T.figures([
        ("Market mood", label, f"mean company score {mkt:+.2f}" if pd.notna(mkt) else "no sessions before price cut-off"),
        ("Headlines", f"{len(items):,}", f"{str(items.first_seen_utc.min())[:10]} – {str(items.first_seen_utc.max())[:10]}"),
        ("Ticker-sessions", f"{len(daily):,}", "with at least one headline"),
        ("Newer than prices", f"{int((items.session > ov['last_date']).sum())}", "headlines after the last price session; not used"),
    ]), unsafe_allow_html=True)
    t = st.selectbox("Company", sorted(daily.ticker.unique()), format_func=lambda x: f"{short(x)} · {names.get(x, 'NIFTY 50 / market')}")
    d = daily[daily.ticker == t].sort_values("session")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d.session, y=d.score, name="Daily score", marker=dict(color=[T.GREEN if v >= 0 else T.ORANGE for v in d.score]),
                         customdata=d.articles, hovertemplate="%{y:+.2f} from %{customdata} headlines<extra></extra>"))
    fig.add_trace(go.Scatter(x=d.session, y=d.momentum_3, name="3-session momentum", mode="lines", line=dict(color=T.INK, width=1.5)))
    fig.add_vline(x=ov["last_date"], line=dict(color=T.NEUTRAL, width=1, dash="dot"))
    chart(T.style(fig, 320, "score (−1 to +1)"))
    st.subheader("Latest headlines")
    x = items[items.ticker == t].sort_values("first_seen_utc", ascending=False).head(25)
    cols = [c for c in ["first_seen_utc", "session", "title", "domain", "vader_compound", "finbert_polarity"] if c in x]
    st.dataframe(x[cols], hide_index=True, width="stretch", column_config={"title": st.column_config.TextColumn(width="large")})
    st.caption("GDELT's free API covers a recent rolling window only, so sentiment cannot train or validate the forecasting models over "
               "2016–2026, and the with/without-sentiment test required by the brief has not been run. Titles and links only are stored.")


# =================== 7. MODEL COMPARISON ===================
def model_comparison():
    reg = c_registry()
    header("Model comparison", "Research view: the eight required models against two simple baselines.",
           [("Validation results", False), ("Test window not evaluated", False)])
    st.subheader("Model availability")
    ready = [m for m in reg.models if m.loaded]; deep_down = [m for m in reg.models if m.family == "Deep" and not m.loaded]
    st.markdown(T.figures([("Models ready", f"{len(ready)} of {len(reg.models)}", "can produce forecasts"),
                           ("Classical", f"{sum(m.family == 'Classical' for m in ready)} of 4", "fitted on the training period"),
                           ("Deep", f"{sum(m.family == 'Deep' for m in ready)} of 4", "PyTorch checkpoints"),
                           ("Selected for decisions", reg.selected or "none", "lowest validation error among ready models")]), unsafe_allow_html=True)
    if deep_down:
        incompatible = all("feature order" in (m.detail or "") for m in deep_down)
        note("Deep-model inference unavailable",
             ("The four deep-model checkpoints from Kaggle are installed but are incompatible with the current feature pipeline: "
              "they were trained with seven extra raw columns (open, high, low, close, volume, dividends, stock splits) that the pipeline "
              "now deliberately excludes. Loading them would mean feeding the models inputs they were not trained on, so they are not used "
              "and no deep-model forecasts are shown. Their validation results below come from the Kaggle experiment."
              if incompatible else "Some deep-model checkpoints could not be loaded, so those models produce no forecasts. Details below."))
    rows = []
    for m in reg.models:
        status, why = model_status(m)
        rows.append({"Model": m.name, "Family": m.family, "Status": status + (" · selected" if m.name == reg.selected else ""),
                     "Validation MAE vs naive": (m.validation_mae / reg.naive_mae - 1) * 100 if m.validation_mae else np.nan, "Explanation": why})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", height=35 * 9 + 3, column_config={
        "Model": st.column_config.TextColumn(width="medium"), "Family": st.column_config.TextColumn(width="small"),
        "Status": st.column_config.TextColumn(width="small"),
        "Validation MAE vs naive": st.column_config.NumberColumn("MAE vs naive", format="%+.2f%%", width="small",
                                                                 help="Experiment-01 validation; positive = worse than the no-change forecast"),
        "Explanation": st.column_config.TextColumn(width="large")})
    with st.expander("Technical details"):
        rt = reg.table()[["name", "family", "loaded", "source", "detail"]]
        st.dataframe(rt.rename(columns={"name": "Model", "family": "Family", "loaded": "Loaded", "source": "Artifact", "detail": "Loader message"}),
                     hide_index=True, width="stretch", column_config={"Loader message": st.column_config.TextColumn(width="large")})
    st.caption("Selection: among models that are ready, the one with the lowest Experiment-01 validation MAE. Classical models are re-fitted "
               "locally on the training period (scripts/persist_classical_models.py); deep checkpoints are read from artifacts/kaggle/models/deep/.")
    if not api.experiment_available():
        return
    e = c_exp(); o, s = e["overall"], e["summary"].set_index("model"); up = s.loc[e["always_up"], "directional_accuracy"]
    note("Finding", f"No trained model beat the naive forecast. The closest, {o.index[0]}, was {o.iloc[0].mae_vs_naive_pct:.2f}% worse on mean "
         "absolute error. Directional accuracy for every model is within one point of 50%.")
    a, b = st.columns(2, gap="large")
    with a:
        st.subheader("Price error vs naive")
        d = o.sort_values("mae_vs_naive_pct", ascending=False)
        fig = go.Figure(go.Bar(x=d.mae_vs_naive_pct, y=d.index, orientation="h", width=0.6, marker=dict(color=T.ORANGE, line=dict(color=T.PAPER, width=2)),
                               text=[f"{v:+.1f}%" for v in d.mae_vs_naive_pct], textposition="outside", textfont=dict(family="Menlo, monospace", size=11),
                               hovertemplate="%{y}: %{x:+.2f}%<extra></extra>"))
        fig.add_vline(x=0, line=dict(color=T.INK, width=1.5))
        T.style(fig, 320, legend=False).update_layout(hovermode="closest")
        fig.update_xaxes(ticksuffix="%", showgrid=True, gridcolor=T.GRID, range=[-2, d.mae_vs_naive_pct.max() * 1.18])
        chart(fig)
    with b:
        st.subheader("Directional accuracy")
        d = o.sort_values("directional_accuracy")
        fig = go.Figure(go.Scatter(x=d.directional_accuracy * 100, y=d.index, mode="markers",
                                   marker=dict(color=T.BLUE, size=11, line=dict(color=T.PAPER, width=2)), hovertemplate="%{y}: %{x:.2f}%<extra></extra>"))
        fig.add_vline(x=up * 100, line=dict(color=T.INK, width=1.5))
        fig.add_annotation(x=up * 100, y=1.05, yref="paper", text=f"always up {up * 100:.1f}%", showarrow=False, font=dict(family="Menlo, monospace", size=11))
        T.style(fig, 320, legend=False).update_layout(hovermode="closest")
        fig.update_xaxes(range=[47.5, 52.5], ticksuffix="%", showgrid=True, gridcolor=T.GRID)
        chart(fig)
    st.subheader("Period by period: error vs naive")
    f = e["by_fold"]; piv = f.pivot(index="model", columns="fold", values="mae_vs_naive_pct").loc[o.index]
    fig = go.Figure(go.Heatmap(z=piv.values, x=list(piv.columns), y=list(piv.index), zmin=-10, zmax=10, colorscale=T.DIVERGING, xgap=2, ygap=2,
                               text=[[f"{v:+.1f}%" for v in row] for row in piv.values], texttemplate="%{text}",
                               textfont=dict(family="Menlo, monospace", size=11), colorbar=dict(thickness=10, len=0.8),
                               hovertemplate="%{y}, %{x}: %{text}<extra></extra>"))
    T.style(fig, 330, legend=False).update_layout(hovermode="closest")
    fig.update_xaxes(side="top", showline=False, ticks=""); fig.update_yaxes(autorange="reversed", showgrid=False, showline=False, ticks="")
    chart(fig)
    st.subheader("Full results (Experiment 01, Kaggle walk-forward)")
    st.dataframe(e["summary"].set_index("model"), width="stretch")
    lv = c_localval()
    if lv is not None:
        st.subheader("Local reproduction of the classical models (single validation split)")
        st.dataframe(lv.set_index("model"), width="stretch")
        st.caption("Fitted on this machine's data build on the training partition and scored on the whole validation partition. Values differ "
                   "slightly from Kaggle because the data download differs.")
    st.markdown("- MAE and RMSE are in rupees, averaged over stock-period results, so high-priced stocks weigh more.\n"
                "- R² near 0.90 is not skill: the naive forecast scores the same.\n"
                "- The naive baseline's 0.5% directional accuracy counts only days with exactly zero return.\n"
                "- Exploratory run: fixed settings, one seed, no confidence intervals; 19 flagged data rows.")


PAGES = dict(zip(PANELS, [overview, price_prediction, recommendations, portfolio, risk_dashboard, sentiment, model_comparison]))
with st.sidebar:
    st.markdown('<div class="ng-kicker">Northgate</div>', unsafe_allow_html=True)
    st.markdown("### Stock Predictor")
    q = st.query_params.get("panel", "")
    page = st.radio("Panel", PANELS, index=PANELS.index(q) if q in PANELS else 0, label_visibility="collapsed")
    st.markdown(f'<div class="ng-foot">{DISCLAIMER}<br><br>Reads saved data and persisted models only; nothing is trained when the app opens.</div>',
                unsafe_allow_html=True)

try:
    PAGES[page]()
except api.DataUnavailable as exc:
    header(page, None, [("Data missing", True)]); note("Data not found", str(exc))
st.markdown(f'<div class="ng-foot">{DISCLAIMER}</div>', unsafe_allow_html=True)

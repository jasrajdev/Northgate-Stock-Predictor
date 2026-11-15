"""Visual language for the dashboard: paper background, ink text, one restrained palette.

Palette validated for colour-vision separation and contrast on the page background
(dataviz validator, light mode): blue, burnt orange, violet, green, in fixed order.
"""
import plotly.graph_objects as go

PAPER, PANEL, INK, MUTED, RULE, GRID = "#FAF8F4", "#F1EDE4", "#1C1B19", "#6B665C", "#1C1B19", "#E4DFD5"
BLUE, ORANGE, VIOLET, GREEN = "#2B6CB0", "#C2571A", "#7B4FA6", "#2F8F6B"
SERIES = [BLUE, ORANGE, VIOLET, GREEN]
NEUTRAL = "#8C867A"
DIVERGING = [[0.0, BLUE], [0.5, "#EDE9E0"], [1.0, ORANGE]]
SEQUENTIAL = [[0.0, "#E9EEF4"], [1.0, "#1F4E86"]]
MONO = "ui-monospace, 'SF Mono', Menlo, Consolas, monospace"
SERIF = "'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif"

CSS = f"""
<style>
.block-container {{ padding-top: 3.4rem; max-width: 1180px; }}
h1, h2, h3 {{ font-family: {SERIF}; font-weight: 600; letter-spacing: -0.01em; color: {INK}; }}
h1 {{ font-size: 2.0rem; border-top: 3px solid {RULE}; padding-top: .7rem; margin-bottom: .1rem; }}
h3 {{ font-size: 1.08rem; border-bottom: 1px solid {RULE}; padding-bottom: .25rem; margin-top: 1.6rem; }}
.ng-kicker {{ font-family: {MONO}; font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: {MUTED}; }}
.ng-lede {{ font-size: 1.02rem; color: #3A3832; max-width: 62rem; margin: .2rem 0 1.1rem 0; }}
.ng-tag {{ display: inline-block; font-family: {MONO}; font-size: .68rem; letter-spacing: .1em; text-transform: uppercase;
          border: 1px solid {INK}; padding: .08rem .45rem; margin-right: .4rem; color: {INK}; background: transparent; }}
.ng-tag.off {{ border-style: dashed; color: {MUTED}; border-color: {MUTED}; }}
.ng-figs {{ display: flex; flex-wrap: wrap; border-top: 1px solid {RULE}; border-bottom: 1px solid {RULE}; margin: .6rem 0 1rem 0; }}
.ng-fig {{ flex: 1 1 150px; padding: .7rem .9rem .6rem 0; margin-right: .9rem; border-right: 1px solid {GRID}; }}
.ng-fig:last-child {{ border-right: 0; }}
.ng-figs.compact .ng-fig {{ flex: 1 1 80px; margin-right: .6rem; padding-right: .6rem; }}
.ng-figs.compact .ng-fig .v {{ font-size: 1.2rem; }}
.ng-fig .v {{ font-family: {MONO}; font-size: 1.45rem; font-variant-numeric: tabular-nums; color: {INK}; line-height: 1.15; }}
.ng-fig .l {{ font-family: {MONO}; font-size: .66rem; letter-spacing: .1em; text-transform: uppercase; color: {MUTED}; }}
.ng-fig .s {{ font-size: .8rem; color: {MUTED}; }}
.ng-note {{ border-left: 3px solid {INK}; background: {PANEL}; padding: .7rem 1rem; margin: .8rem 0; font-size: .95rem; }}
.ng-note b {{ font-family: {MONO}; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; }}
.ng-foot {{ font-family: {MONO}; font-size: .68rem; color: {MUTED}; border-top: 1px solid {GRID}; margin-top: 2.5rem; padding-top: .6rem; }}
[data-testid="stSidebar"] {{ border-right: 1px solid {RULE}; }}
[data-testid="stSidebar"] label p {{ font-size: .95rem; }}
[data-testid="stDataFrame"] * {{ font-variant-numeric: tabular-nums; }}
.ng-reasons {{ margin: .2rem 0 1rem 0; }}
.ng-reasons .r {{ display: grid; grid-template-columns: 7.5rem 4.5rem 1fr; gap: .9rem; padding: .45rem 0; border-bottom: 1px solid {GRID}; font-size: .92rem; }}
.ng-reasons .t {{ font-family: {MONO}; font-size: .8rem; color: {INK}; }}
.ng-reasons .a {{ font-family: {MONO}; font-size: .72rem; letter-spacing: .08em; }}
.ng-reasons .w {{ color: #3A3832; }}
.ng-steps {{ display: flex; flex-wrap: wrap; gap: .8rem; margin: .6rem 0 1.2rem 0; }}
.ng-step {{ flex: 1 1 200px; border: 1px solid {GRID}; border-top: 2px solid {INK}; padding: .7rem .9rem; background: {PAPER}; }}
.ng-step.off {{ border-top: 2px dashed {MUTED}; }}
.ng-step .n {{ font-family: {MONO}; font-size: .66rem; letter-spacing: .12em; text-transform: uppercase; color: {MUTED}; }}
.ng-step .h {{ font-family: {SERIF}; font-weight: 600; font-size: 1.02rem; margin: .15rem 0 .25rem 0; }}
.ng-step .b {{ font-size: .86rem; color: #3A3832; }}
.ng-step .s {{ font-family: {MONO}; font-size: .68rem; letter-spacing: .08em; text-transform: uppercase; margin-top: .45rem; }}
.ng-code {{ font-family: {MONO}; font-size: .8rem; background: {PANEL}; border: 1px solid {GRID}; padding: .6rem .8rem; margin-bottom: .6rem; white-space: pre; overflow-x: auto; }}
</style>
"""


def style(fig: go.Figure, height: int = 360, y_title: str | None = None, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height, paper_bgcolor=PAPER, plot_bgcolor=PAPER, margin=dict(l=8, r=16, t=34 if legend else 12, b=8),
        font=dict(family="Georgia, serif", size=13, color=INK), hovermode="x unified", showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=PAPER, bordercolor=INK, font=dict(family="Menlo, monospace", size=12, color=INK)),
    )
    axis = dict(showgrid=True, gridcolor=GRID, gridwidth=1, zeroline=False, linecolor=NEUTRAL, ticks="outside",
                tickcolor=NEUTRAL, ticklen=4, tickfont=dict(family="Menlo, monospace", size=11, color=MUTED))
    fig.update_xaxes(**{**axis, "showgrid": False})
    fig.update_yaxes(**axis, title=dict(text=y_title or "", font=dict(size=12, color=MUTED)))
    return fig


def figures(items, compact: bool = False) -> str:
    """items: (label, value, sub) tuples -> HTML strip of headline figures. `compact` keeps
    the strip on one line inside narrow columns."""
    cells = "".join(f'<div class="ng-fig"><div class="l">{l}</div><div class="v">{v}</div><div class="s">{s}</div></div>' for l, v, s in items)
    return f'<div class="ng-figs{" compact" if compact else ""}">{cells}</div>'


def tag(text: str, off: bool = False) -> str:
    return f'<span class="ng-tag{" off" if off else ""}">{text}</span>'


def steps(items) -> str:
    """items: (number label, heading, body, status text, done) -> row of pipeline-step cards."""
    cells = "".join(f'<div class="ng-step{"" if done else " off"}"><div class="n">{n}</div><div class="h">{h}</div>'
                    f'<div class="b">{b}</div><div class="s" style="color:{INK if done else MUTED}">{st}</div></div>'
                    for n, h, b, st, done in items)
    return f'<div class="ng-steps">{cells}</div>'


def reasons(rows) -> str:
    """rows: (ticker, action, colour, text) -> aligned list of decision explanations."""
    body = "".join(f'<div class="r"><span class="t">{t}</span><span class="a" style="color:{c}">{a}</span><span class="w">{w}</span></div>'
                   for t, a, c, w in rows)
    return f'<div class="ng-reasons">{body}</div>'

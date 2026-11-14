"""READ-ONLY: validate NSE Bhavcopy files and compare with original Yahoo CSVs."""
from pathlib import Path
import csv, io, zipfile, hashlib
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1]
EV = OUT / "evidence"
BH = ROOT / "data/raw/nse_bhavcopy"
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)

REPORTED = {
 "cm22APR2019bhav.csv.zip": "73747d17e27a6acf1fd5a976657110fa76b61611bff32a3e9a9ff38daaaff29d",
 "cm23APR2019bhav.csv.zip": "5783418c132bfa72661a7e34a76cecc88c1f5654d9321e5bec0f5a5355f84b7e",
 "cm12MAY2020bhav.csv.zip": "78c24010e0f6510a2426cfbbcc663bb868cc37003b128c3126f9c64fda9aae16",
 "cm13MAY2020bhav.csv.zip": "36589b0e763079ccb3599443b37c51ba361d6e97b0c59e6264f73444f4daae44",
 "cm14MAY2020bhav.csv.zip": "66cb0bdbee5a861287cbddbdd4ab2a58a2164cef088e4f563ef53a83d25d8654",
 "sec_bhavdata_full_25102024.csv": "e889503392d34424785be117156656b0fc6b554d26d6d195ae06f92ce0279904",
 "sec_bhavdata_full_28102024.csv": "2ea975e4b0568e33de01c8f55ae96aa0cc8a35a11aab35074e6143aba051d1ef",
 "sec_bhavdata_full_29102024.csv": "871dd93f5925c6f8a4656523d48f70f8199ec0872c761a2dc290fbdd082dacf1",
 "sec_bhavdata_full_25082025.csv": "7ad26f0874f9c67199da34e1f0f000b9827f26947202fbf1dce763d6ceabe46f",
 "sec_bhavdata_full_26082025.csv": "996347736726a5abc34d0d9a3629c76c8880c3bca3bbff7589dff32c9aed8675",
 "sec_bhavdata_full_28082025.csv": "4af5d67891bc90b3e4213367bd2f2566cc2f45fbcf55ac11ae9e78715d259c8f",
}
WANT = {"cm22APR2019": "BHARTIARTL", "cm23APR2019": "BHARTIARTL", "cm12MAY2020": "RELIANCE", "cm13MAY2020": "RELIANCE",
        "cm14MAY2020": "RELIANCE", "25102024": "RELIANCE", "28102024": "RELIANCE", "29102024": "RELIANCE",
        "25082025": "HDFCBANK", "26082025": "HDFCBANK", "28082025": "HDFCBANK"}
UNIVERSE = ["BHARTIARTL", "HDFCBANK", "HINDUNILVR", "ICICIBANK", "INFY", "ITC", "LT", "RELIANCE", "SUNPHARMA", "TCS"]

yahoo = pd.read_csv(ROOT / "data/processed/market_panel.csv", parse_dates=["Date"])
recs, filechecks = [], []
for f in sorted(list(BH.glob("*.zip")) + list((BH / "bonus_audit").glob("*.csv"))):
    raw = f.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    chk = dict(file=str(f.relative_to(ROOT)), bytes=len(raw), sha256=sha, sha_matches_documented=(sha == REPORTED.get(f.name)))
    if f.suffix == ".zip":
        z = zipfile.ZipFile(io.BytesIO(raw)); chk["zip_ok"] = z.testzip() is None
        name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        text = z.read(name).decode("utf-8-sig"); chk["inner"] = name
    else:
        text = raw.decode("utf-8-sig"); chk["zip_ok"] = None
        chk["looks_like_html"] = text.lstrip()[:1] == "<"
    df = pd.read_csv(io.StringIO(text), skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, [c for c in df.columns if c and not c.startswith("Unnamed")]]
    for c in df.select_dtypes(include=["object","str"]): df[c] = df[c].str.strip()
    legacy = "TIMESTAMP" in df.columns
    datecol = "TIMESTAMP" if legacy else "DATE1"
    dates = pd.to_datetime(df[datecol], format="%d-%b-%Y").dt.date.unique()
    chk.update(schema="legacy_cm_bhav" if legacy else "sec_bhavdata_full", columns="|".join(df.columns), rows=len(df),
               distinct_dates=";".join(map(str, dates)), series_counts=str(df.SERIES.value_counts().head(4).to_dict()))
    key = next(k for k in WANT if k in f.name)
    cm = dict(OPEN="OPEN", HIGH="HIGH", LOW="LOW", CLOSE="CLOSE", PREV="PREVCLOSE", VOL="TOTTRDQTY") if legacy else \
         dict(OPEN="OPEN_PRICE", HIGH="HIGH_PRICE", LOW="LOW_PRICE", CLOSE="CLOSE_PRICE", PREV="PREV_CLOSE", VOL="TTL_TRD_QNTY")
    eqrows = df[(df.SERIES == "EQ") & (df.SYMBOL.isin(UNIVERSE))]
    chk["universe_eq_rows"] = len(eqrows); chk["target_eq_rows"] = int((eqrows.SYMBOL == WANT[key]).sum())
    filechecks.append(chk)
    for _, r in eqrows.iterrows():
        d = pd.Timestamp(dates[0]); y = yahoo[(yahoo.Ticker == r.SYMBOL + ".NS") & (yahoo.Date == d)]
        rec = dict(date=str(d.date()), symbol=r.SYMBOL, is_event_target=(r.SYMBOL == WANT[key]), nse_file=f.name,
                   nse_open=float(r[cm["OPEN"]]), nse_high=float(r[cm["HIGH"]]), nse_low=float(r[cm["LOW"]]), nse_close=float(r[cm["CLOSE"]]),
                   nse_prev_close=float(r[cm["PREV"]]), nse_volume=int(r[cm["VOL"]]), isin=r.get("ISIN", ""))
        if len(y):
            y = y.iloc[0]
            rec.update(yahoo_open=y.Open, yahoo_high=y.High, yahoo_low=y.Low, yahoo_close=y.Close, yahoo_adj_close=y["Adj Close"], yahoo_volume=int(y.Volume),
                       ratio_yahoo_close_to_nse_close=y.Close / float(r[cm["CLOSE"]]), ratio_yahoo_open_to_nse_open=y.Open / float(r[cm["OPEN"]]),
                       ratio_yahoo_high_to_nse_high=y.High / float(r[cm["HIGH"]]), ratio_yahoo_low_to_nse_low=y.Low / float(r[cm["LOW"]]),
                       ratio_yahoo_volume_to_nse_volume=(y.Volume / int(r[cm["VOL"]])) if int(r[cm["VOL"]]) else np.nan)
        recs.append(rec)
fc = pd.DataFrame(filechecks); fc.to_csv(EV / "bhavcopy_file_validation.csv", index=False)
print(fc.drop(columns=["columns", "sha256"]).to_string())
print("schemas:", fc.groupby("schema")["columns"].first().to_dict())
cmp = pd.DataFrame(recs).sort_values(["symbol", "date"])
cmp.to_csv(EV / "nse_vs_yahoo_all_universe_rows.csv", index=False)
cols = ["date", "symbol", "is_event_target", "nse_close", "yahoo_close", "yahoo_adj_close", "ratio_yahoo_close_to_nse_close", "ratio_yahoo_open_to_nse_open", "ratio_yahoo_high_to_nse_high", "ratio_yahoo_low_to_nse_low", "ratio_yahoo_volume_to_nse_volume"]
print("\nALL UNIVERSE EQ ROWS FOUND IN THE 11 OFFICIAL FILES vs YAHOO")
print(cmp[cols].round(5).to_string(index=False))

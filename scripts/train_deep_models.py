"""Train PRD deep sequence models on GPU when available; validation only.

Target is next-session log return, converted back to predicted adjusted close
for PRD-compatible MAE/RMSE/directional metrics. Final test CSV is never loaded.
"""
from __future__ import annotations
import json, random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parents[1]
SPLITS=ROOT/"data"/"processed"/"splits"
OUT=ROOT/"models"/"deep"
REPORT=ROOT/"reports"/"validation"
SEQ=30
EPOCHS=40
BATCH=128
PATIENCE=8
SEED=42

def seed_all():
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(SEED)

class Recurrent(nn.Module):
    def __init__(self, kind, n_features, hidden=64):
        super().__init__()
        cls={"LSTM":nn.LSTM,"GRU":nn.GRU,"BiLSTM":nn.LSTM}[kind]
        bidir=kind=="BiLSTM"
        self.rnn=cls(n_features,hidden,num_layers=2,batch_first=True,
                     dropout=0.2,bidirectional=bidir)
        self.head=nn.Sequential(nn.Dropout(.2),nn.Linear(hidden*(2 if bidir else 1),32),
                                 nn.ReLU(),nn.Linear(32,1))
    def forward(self,x):
        z,_=self.rnn(x)
        return self.head(z[:,-1]).squeeze(-1)

class TransformerRegressor(nn.Module):
    def __init__(self,n_features,d=64,heads=4):
        super().__init__()
        self.proj=nn.Linear(n_features,d)
        self.pos=nn.Parameter(torch.zeros(1,SEQ,d))
        layer=nn.TransformerEncoderLayer(d_model=d,nhead=heads,
              dim_feedforward=128,dropout=.15,batch_first=True,activation="gelu")
        self.encoder=nn.TransformerEncoder(layer,num_layers=2)
        self.head=nn.Sequential(nn.LayerNorm(d),nn.Linear(d,32),nn.GELU(),nn.Linear(32,1))
    def forward(self,x):
        z=self.proj(x)+self.pos
        return self.head(self.encoder(z)[:,-1]).squeeze(-1)

def make_sequences(frame, feature_cols, ticker_map, medians, means, stds, fit=False):
    X=[]; y=[]; px=[]; dates=[]
    for ticker,g in frame.groupby("Ticker",sort=False):
        g=g.sort_values("Date")
        a=g[feature_cols].replace([np.inf,-np.inf],np.nan).fillna(medians)
        a=((a-means)/stds).clip(-10,10).to_numpy(dtype=np.float32)
        one=np.zeros(len(ticker_map),dtype=np.float32); one[ticker_map[ticker]]=1
        onehot=np.repeat(one[None,:],len(g),axis=0)
        a=np.concatenate([a,onehot],axis=1)
        ret=pd.to_numeric(g["target_log_return_t1"],errors="coerce").to_numpy()
        cur=pd.to_numeric(g["Adj Close"],errors="coerce").to_numpy()
        dt=pd.to_datetime(g["Date"]).to_numpy()
        for i in range(SEQ-1,len(g)):
            if not np.isfinite(ret[i]) or not np.isfinite(cur[i]) or cur[i]<=0: continue
            X.append(a[i-SEQ+1:i+1]); y.append(ret[i]); px.append(cur[i]); dates.append(dt[i])
    if not X: raise RuntimeError("No sequences built; check split length and feature completeness.")
    return (np.asarray(X,dtype=np.float32),np.asarray(y,dtype=np.float32),
            np.asarray(px,dtype=np.float64),np.asarray(dates))

def evaluate(y,pred,current):
    actual_price=current*np.exp(y); predicted_price=current*np.exp(pred)
    return {
      "mae":float(mean_absolute_error(actual_price,predicted_price)),
      "rmse":float(np.sqrt(mean_squared_error(actual_price,predicted_price))),
      "mape_pct":float(np.mean(np.abs((actual_price-predicted_price)/actual_price))*100),
      "r2":float(r2_score(actual_price,predicted_price)),
      "directional_accuracy":float(np.mean(np.sign(y)==np.sign(pred))),
    }

def train_one(name,model,train_data,val_data,device):
    X,y,_,_=train_data; Xv,yv,pv,_=val_data
    loader=DataLoader(TensorDataset(torch.from_numpy(X),torch.from_numpy(y)),
                      batch_size=BATCH,shuffle=True,pin_memory=device.type=="cuda")
    xv=torch.from_numpy(Xv).to(device); yvt=torch.from_numpy(yv).to(device)
    model.to(device); opt=torch.optim.AdamW(model.parameters(),lr=1e-3,weight_decay=1e-4)
    loss_fn=nn.HuberLoss()
    best=float("inf"); best_state=None; stale=0; history=[]
    for epoch in range(EPOCHS):
        model.train(); losses=[]
        for xb,yb in loader:
            xb=xb.to(device,non_blocking=True); yb=yb.to(device,non_blocking=True)
            opt.zero_grad(set_to_none=True); loss=loss_fn(model(xb),yb)
            loss.backward(); nn.utils.clip_grad_norm_(model.parameters(),1.0); opt.step()
            losses.append(float(loss.detach().cpu()))
        model.eval()
        with torch.no_grad(): vl=float(loss_fn(model(xv),yvt).cpu())
        history.append({"epoch":epoch+1,"train_loss":float(np.mean(losses)),"val_loss":vl})
        if vl<best:
            best=vl; stale=0
            best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}
        else:
            stale+=1
            if stale>=PATIENCE: break
    model.load_state_dict(best_state); model.eval()
    with torch.no_grad(): pred=model(xv).cpu().numpy()
    torch.save({"state_dict":best_state,"model":name,"feature_count":X.shape[2],
                "sequence_length":SEQ,"ticker_map":ticker_map_global},
               OUT/f"{name.lower()}_best.pt")
    return evaluate(yv,pred,pv),history

ticker_map_global={}

def main():
    seed_all()
    train=pd.read_csv(SPLITS/"train.csv",parse_dates=["Date"])
    val=pd.read_csv(SPLITS/"validation.csv",parse_dates=["Date"])
    train=train[train.Ticker!="^NSEI"].copy()
    val=val[val.Ticker!="^NSEI"].copy()
    tickers=sorted(set(train.Ticker)&set(val.Ticker))
    train=train[train.Ticker.isin(tickers)].copy()
    val=val[val.Ticker.isin(tickers)].copy()
    global ticker_map_global
    ticker_map_global={t:i for i,t in enumerate(tickers)}
    excluded={"Date","Ticker","Name","target_date_t1","target_adj_close_t1",
              "target_log_return_t1","target_direction_t1"}
    features=[c for c in train.select_dtypes(include=[np.number]).columns if c not in excluded]
    features=[c for c in features if c in val.columns]
    trnum=train[features].replace([np.inf,-np.inf],np.nan)
    med=trnum.median().fillna(0); means=trnum.fillna(med).mean()
    stds=trnum.fillna(med).std().replace(0,1).fillna(1)
    # Fit imputation/scaling parameters on training rows only.
    tr=make_sequences(train,features,ticker_map_global,med,means,stds)
    va=make_sequences(val,features,ticker_map_global,med,means,stds)
    device=torch.device("cuda" if torch.cuda.is_available() else "cpu")
    OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
    results=[]; histories={}
    constructors={
      "LSTM":lambda n:Recurrent("LSTM",n),
      "GRU":lambda n:Recurrent("GRU",n),
      "BiLSTM":lambda n:Recurrent("BiLSTM",n),
      "Transformer":lambda n:TransformerRegressor(n),
    }
    for name,build in constructors.items():
        model=build(tr[0].shape[2])
        metrics,history=train_one(name,model,tr,va,device)
        results.append({"model":name,"device":str(device),**metrics})
        histories[name]=history
        print(name,metrics)
    pd.DataFrame(results).to_csv(REPORT/"deep_model_comparison_validation.csv",index=False)
    (REPORT/"deep_training_history.json").write_text(json.dumps(histories,indent=2))
    (REPORT/"deep_training_report.json").write_text(json.dumps({
      "device":str(device),"cuda_available":torch.cuda.is_available(),
      "gpu_name":torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
      "sequence_length":SEQ,"feature_count":len(features),"features":features,
      "tickers":tickers,"train_sequences":len(tr[0]),"validation_sequences":len(va[0]),
      "test_partition_loaded":False,"target":"next-session log return; converted to adjusted-close prediction",
      "preprocessing_fit_on_training_only":True,
      "results":results,
    },indent=2))
    print("Final test partition was not loaded.")

if __name__=="__main__": main()

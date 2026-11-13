# GPU Laptop Training Handoff

## Hardware confirmed from the user's 2026-11-13 PowerShell screenshot

- Machine: HP Victus, Windows PowerShell.
- GPU: NVIDIA GeForce RTX 3050 Laptop GPU.
- Dedicated VRAM: 4,094 MiB (4 GiB).
- NVIDIA driver: 592.82.
- Driver-reported CUDA compatibility: 13.1.

The current official PyTorch release (2.14.1) provides CUDA 12.6, 13.0 and 13.2 Windows wheels. The laptop reports driver CUDA 13.1, so use the CUDA 12.6 wheel: it is supported by this newer driver and avoids requiring CUDA 13.2 driver support. The GPU is Ampere (RTX 3050), supported by CUDA 12.6.

## What is ready

The repository can rebuild a first **price/volume-only baseline experiment** for ten provisional Indian equities plus NIFTY 50, with daily OHLCV/adjusted close, 24 backward-looking features, next-session labels, and target-date chronological train/validation/test splits.

- `config/northgate_universe.json`: provisional universe and split settings.
- `scripts/prepare_gpu_training_data.py`: downloads and rebuilds all price/volume data locally.
- `scripts/train_baseline_models.py`: Ridge, Random Forest, SVR and XGBoost; validation only; compares with naive last-adjusted-close.
- `scripts/train_deep_models.py`: LSTM, GRU, BiLSTM and Transformer; validation only; final test partition is never loaded. Defaults are reduced for 4 GB VRAM (batch 16, hidden size 32, one recurrent/encoder layer, sequence length 30, mixed precision on CUDA).

**Important:** the raw and processed CSVs previously generated on the Mac are not committed to GitHub. The Victus rebuilds them from the scripts. This avoids assuming the data files are already downloadable and avoids redistributing vendor data.

## Exact Windows PowerShell steps

Run these commands in a new PowerShell window. Do not paste the `PS C:\...` prompt itself.

### 1. Clone or update the repository

If the folder does not exist:

```powershell
git clone https://github.com/jasrajdev/Northgate-Stock-Predictor.git
cd Northgate-Stock-Predictor
```

If it already exists:

```powershell
cd $HOME\Northgate-Stock-Predictor
git pull origin main
```

### 2. Create the Python environment

Install 64-bit Python 3.11 first if it is not already installed. Then:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks activation, run this once in that PowerShell window and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install project dependencies and CUDA PyTorch

```powershell
python -m pip install -r requirements.txt
python -m pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu126
```

Verify CUDA before downloading data:

```powershell
python -c "import torch; print('PyTorch:',torch.__version__); print('CUDA build:',torch.version.cuda); print('CUDA available:',torch.cuda.is_available()); print('GPU:',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NOT DETECTED'); print('VRAM GiB:',round(torch.cuda.get_device_properties(0).total_memory/1024**3,2) if torch.cuda.is_available() else 'n/a')"
```

**Stop and send me the output if `CUDA available: False` or the GPU is not detected.** Do not start deep training until this check passes.

### 4. Rebuild the dataset on the Victus

```powershell
python scripts/prepare_gpu_training_data.py
```

This downloads the ten equities and NIFTY 50 and creates:
- `data/processed/market_panel.csv`
- `data/processed/feature_panel.csv`
- `data/processed/modeling_dataset_next_day.csv`
- `data/processed/splits/train.csv`
- `data/processed/splits/validation.csv`
- `data/processed/splits/test.csv`
- `reports/data_quality/gpu_data_build_report.json`

Check that the script reports zero duplicate ticker/date keys, all target dates after feature dates, zero missing targets, and all rows assigned once. Do not open or use the test CSV for model selection.

### 5. Run classical baselines first

```powershell
python scripts/train_baseline_models.py
```

This fits Ridge, Random Forest, SVR and XGBoost (CUDA is attempted; XGBoost may fall back to CPU if the installed build cannot use CUDA). It compares all models against the naive last-adjusted-close forecast on validation data only.

### 6. Run deep models

The conservative defaults are appropriate for the confirmed 4 GB RTX 3050:

- sequence length: 30 sessions
- batch size: 16
- hidden size: 32
- one recurrent/Transformer layer
- 30 maximum epochs, early stopping patience 6
- CUDA mixed precision enabled when CUDA is detected

```powershell
python scripts/train_deep_models.py
```

If CUDA runs out of memory, rerun with smaller settings:

```powershell
$env:NORTHGATE_BATCH_SIZE="8"
$env:NORTHGATE_HIDDEN_SIZE="24"
python scripts/train_deep_models.py
```

To restore defaults in the current PowerShell session:

```powershell
Remove-Item Env:NORTHGATE_BATCH_SIZE -ErrorAction SilentlyContinue
Remove-Item Env:NORTHGATE_HIDDEN_SIZE -ErrorAction SilentlyContinue
```

### 7. Send back these outputs

Upload or paste:
- `reports/data_quality/gpu_data_build_report.json`
- `reports/validation/model_summary_validation.csv`
- `reports/validation/deep_model_comparison_validation.csv`
- `reports/validation/deep_training_report.json`
- Full output of `nvidia-smi` and the PyTorch CUDA verification command

Model checkpoints are saved locally under `models/deep/`. Do not upload large model files to GitHub unless specifically requested; keep them backed up separately.

## Dataset limitations — not hidden

This is **baseline-trainable, not PRD-complete**. Still outstanding:
- CPI/macro variables with actual release timestamps and historical vintages.
- Volatility/sector/breadth context series.
- Timestamped historical company and market news, FinBERT/VADER sentiment and an ablation against the price-only baseline.
- Point-in-time historical constituents / delisted equities to address survivorship bias.
- Official-source adjusted-price validation and full EDA/finance-math checks.
- Multi-day targets; horizons and purge/embargo rules are not yet agreed.

Commodity prices are not an explicit mandatory series in PRD v1.0 and are not a blocker for this first training run.

## Reproducibility and evaluation safeguards

- Training and validation only are loaded by both model scripts; the final test file is not opened.
- The chronological split is assigned by target date.
- Learned preprocessing is fit on training rows only in the deep-learning script.
- Compare all models on identical validation dates and targets.
- Do not report validation results as final out-of-sample performance. Freeze choices before evaluating the reserved test set.
- No profit or accuracy is promised.

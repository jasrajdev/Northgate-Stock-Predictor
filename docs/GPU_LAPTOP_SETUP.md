# GPU Laptop Training Handoff

## What is ready

The first reproducible experiment uses ten provisional Indian equities plus NIFTY 50, daily OHLCV and adjusted close, 24 backward-looking price/volume features, and the next observed session's adjusted close as target.

The repository includes:
- `config/northgate_universe.json`: the exact provisional universe and date/split settings.
- `scripts/prepare_gpu_training_data.py`: downloads and rebuilds raw/processed price data, features, labels, and chronological splits.
- `scripts/train_baseline_models.py`: fits per-equity Ridge, Random Forest, SVR and XGBoost; compares against last adjusted close; uses validation only and does not load the final test set.

## Important: what is NOT in the GitHub repository

The Mac's generated CSVs are not committed. The uploaded `market_panel.csv` was inspected in the ChatGPT project: 29,484 rows, 11 tickers (ten equities and `^NSEI`), 2016 onward. But only the raw market panel was uploaded to this conversation; the 17 MB feature panel and 18 MB labelled modelling dataset remain local to the Mac and were not found in the GitHub repository. Therefore the GPU laptop must rebuild them using the committed preparation script. Do not assume the CSVs are already downloadable from GitHub.

Raw Yahoo Finance downloads are not committed because redistribution terms/rights have not been established. The script recreates the dataset on the machine where it is run.

## GPU laptop setup

1. Install 64-bit Python 3.11 or 3.12 and Git.
2. Install the current NVIDIA driver. Open a terminal and run `nvidia-smi`; record the exact GPU name and driver/CUDA version.
3. Clone the repository:
   ```bash
   git clone https://github.com/jasrajdev/Northgate-Stock-Predictor.git
   cd Northgate-Stock-Predictor
   ```
4. Create and activate a virtual environment:
   - Windows PowerShell:
     ```powershell
     py -3.11 -m venv .venv
     .venv\Scripts\Activate.ps1
     python -m pip install --upgrade pip
     ```
   - Linux:
     ```bash
     python3.11 -m venv .venv
     source .venv/bin/activate
     python -m pip install --upgrade pip
     ```
5. Install project requirements:
   ```bash
   pip install -r requirements.txt
   ```
6. Rebuild the first dataset:
   ```bash
   python scripts/prepare_gpu_training_data.py
   ```
7. Train and compare classical baselines:
   ```bash
   python scripts/train_baseline_models.py
   ```
8. Send the contents of `reports/data_quality/gpu_data_build_report.json`, `reports/validation/model_summary_validation.csv`, and the `nvidia-smi` output back for review.

## GPU expectations

The current Ridge, Random Forest and SVR implementations use scikit-learn and run on CPU. XGBoost can use CUDA only when the installed XGBoost build and NVIDIA driver support it; verify the actual GPU before assuming acceleration. The first script is a baseline comparison, not yet the PRD's four deep-learning architectures. Do not install TensorFlow/PyTorch CUDA packages blindly before identifying the GPU and OS.

## Data limitations still open

- CPI 2024 series and the official linked back series; old and new base-year series must not be concatenated without documented linking.
- RBI/FRED macro series with actual release timestamps/vintages; forward-filling by observation month alone can leak.
- Historical timestamped company/market news across the full period. GDELT has a large historical archive but is broad news metadata, not a guaranteed complete financial-news archive or article-text corpus.
- FinBERT and VADER daily sentiment features, aligned to the next eligible session after market close.
- Point-in-time historical constituents / delisted stocks to address survivorship bias.
- Multi-day labels, which require an explicit horizon and purge/embargo rules.

## Reproducibility and safety

The final six-calendar-month test partition is reserved. Tune only on training/validation. The training script must never read `splits/test.csv` until model selection is frozen. No profit or accuracy is promised.

"""Northgate Stock Predictor research package."""
import os as _os

# PyTorch and scikit-learn/XGBoost each bundle their own OpenMP runtime on macOS. Using both
# in one process segfaults unless OpenMP is single-threaded, so set it before either loads.
_os.environ.setdefault("OMP_NUM_THREADS", "1")

__version__ = "0.2.0"

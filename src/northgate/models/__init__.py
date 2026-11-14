"""Model families: four classical (scikit-learn / XGBoost) and four deep (PyTorch)."""
CLASSICAL = ["Ridge", "RandomForest", "SVR_RBF", "XGBoost"]
DEEP = ["LSTM", "GRU", "BiLSTM", "Transformer"]
ALL = CLASSICAL + DEEP

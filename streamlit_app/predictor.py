# streamlit_app/predictor.py
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error


FEATURES = ["rating"]          # <-- tak ada lagi "sold_count" di sini
TARGET   = "sold_count"


@dataclass
class ModelInfo:
    model: LinearRegression
    r2: float
    mae: float


def _prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Bersihkan kolom yang dibutuhkan saja & drop NaN."""
    usecols = FEATURES + [TARGET]
    clean = df[usecols].dropna().copy()
    return clean.astype(float)


def train_model(df: pd.DataFrame) -> ModelInfo:
    data = _prepare(df)
    X = data[FEATURES]
    y = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    reg = LinearRegression().fit(X_train, y_train)

    return ModelInfo(
        model=reg,
        r2=r2_score(y_test, reg.predict(X_test)),
        mae=mean_absolute_error(y_test, reg.predict(X_test)),
    )


def predict_sales(model: LinearRegression, rating: float) -> float:
    """Kembalikan prediksi sold_count berikutnya berdasarkan rating."""
    X_new = np.array([[rating]])
    return float(model.predict(X_new)[0])

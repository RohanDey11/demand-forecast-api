"""
Evaluate SARIMA baseline for comparison
"""
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error

DATA_PATH = Path(__file__).parent.parent / "data" / "weekly_sales.csv"

def load_and_clean():
    df = pd.read_csv(DATA_PATH)
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds")
    if (df["y"] == 0).any():
        df["y"] = df["y"].replace(0, np.nan)
        df["y"] = df["y"].interpolate().bfill().ffill()
    df = df.set_index("ds")
    return df

def eval_sarima():
    df = load_and_clean()
    train = df.iloc[:-22]
    test = df.iloc[-22:]

    # SARIMA(1,1,1)(1,1,1,52) - yearly seasonality 52 weeks
    model = SARIMAX(train["y"], order=(1,1,1), seasonal_order=(1,1,1,52))
    res = model.fit(disp=False)

    pred = res.get_forecast(steps=22).predicted_mean

    mape = np.mean(np.abs((test["y"].values - pred.values) / test["y"].values)) * 100
    rmse = np.sqrt(mean_squared_error(test["y"].values, pred.values))

    print(f"SARIMA MAPE: {mape:.2f}%")
    print(f"SARIMA RMSE: {rmse:,.2f}")

if __name__ == "__main__":
    eval_sarima()

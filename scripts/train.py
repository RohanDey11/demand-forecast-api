"""
Train Prophet model and save metrics
Reproducible evaluation for README metrics
"""
import pandas as pd
import numpy as np
from pathlib import Path
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import json

DATA_PATH = Path(__file__).parent.parent / "data" / "weekly_sales.csv"

def load_and_clean():
    df = pd.read_csv(DATA_PATH)
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.sort_values("ds")
    # Interpolate known gap week (Online Retail II Christmas reporting gap)
    if (df["y"] == 0).any():
        print(f"Found {(df['y']==0).sum()} zero rows, interpolating")
        df["y"] = df["y"].replace(0, np.nan)
        df["y"] = df["y"].interpolate(method="linear").bfill().ffill()
    return df

def train_eval():
    df = load_and_clean()
    print(f"Loaded {len(df)} weeks from {df['ds'].min()} to {df['ds'].max()}")

    # 84 train / 22 test split (same as notebook)
    train = df.iloc[:-22]
    test = df.iloc[-22:]

    print(f"Train: {len(train)}, Test: {len(test)}")

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        interval_width=0.95,
        changepoint_prior_scale=0.5,
        seasonality_prior_scale=10.0,
    )
    try:
        model.add_country_holidays(country_name="UK")
    except:
        pass

    model.fit(train)

    future = model.make_future_dataframe(periods=22, freq="W")
    forecast = model.predict(future)
    pred = forecast.tail(22)["yhat"].values

    mape = np.mean(np.abs((test["y"].values - pred) / test["y"].values)) * 100
    rmse = np.sqrt(mean_squared_error(test["y"].values, pred))

    print(f"Prophet MAPE: {mape:.2f}%")
    print(f"Prophet RMSE: {rmse:,.2f}")

    # Save metrics for README
    metrics = {
        "weeks_history": len(df),
        "train_weeks": len(train),
        "test_weeks": len(test),
        "prophet_mape": round(float(mape), 2),
        "prophet_rmse": round(float(rmse), 2),
        "config": {
            "yearly_seasonality": True,
            "weekly_seasonality": False,
            "seasonality_mode": "multiplicative"
        },
        "data_cleaning": "Linear interpolation for 2010-12-26 gap (was 0, now interpolated)"
    }

    with open(Path(__file__).parent / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Saved metrics.json")

if __name__ == "__main__":
    train_eval()

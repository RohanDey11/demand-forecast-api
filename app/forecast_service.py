from pathlib import Path
from datetime import datetime
import logging

import pandas as pd
from prophet import Prophet

logger = logging.getLogger(__name__)

PROPHET_CONFIG = {
    "yearly_seasonality": True,
    "weekly_seasonality": False,
    "daily_seasonality": False,
    "seasonality_mode": "multiplicative",
    "interval_width": 0.95,
}

BEST_PARAMS = {
    "changepoint_prior_scale": 0.5,
    "seasonality_prior_scale": 10.0,
}

_cached_forecast = None
_last_refit = None
_last_history_date = None
_weeks_history = 0

DATA_PATH = Path(__file__).parent.parent / "data" / "weekly_sales.csv"
if not DATA_PATH.exists():
    DATA_PATH = Path("/app/data/weekly_sales.csv")


def load_weekly_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["ds"] = pd.to_datetime(df["ds"])
    return df.sort_values("ds")


def fit_and_cache() -> bool:
    global _cached_forecast, _last_refit, _last_history_date, _weeks_history

    logger.info("Fitting Prophet model")
    df = load_weekly_data()
    _weeks_history = len(df)

    model = Prophet(**PROPHET_CONFIG, **BEST_PARAMS)
    try:
        model.add_country_holidays(country_name="UK")
    except Exception:
        logger.warning("UK holidays unavailable, continuing without them")

    model.fit(df)
    future = model.make_future_dataframe(periods=22, freq="W")
    _cached_forecast = model.predict(future)

    _last_refit = datetime.utcnow().isoformat() + "Z"
    _last_history_date = df["ds"].max()

    logger.info(f"Model fitted, {len(_cached_forecast)} rows cached")
    return True


def get_cached_forecast(horizon: int) -> pd.DataFrame:
    global _cached_forecast

    if _cached_forecast is None:
        try:
            fit_and_cache()
        except Exception as exc:
            logger.error(f"Refit on cache miss failed: {exc}")
            raise RuntimeError("Model is warming up, please retry in 30s") from exc

    if not 1 <= horizon <= 22:
        raise ValueError("horizon_weeks must be between 1 and 22")

    return _cached_forecast.tail(22).head(horizon)[["ds", "yhat", "yhat_lower", "yhat_upper"]]


def get_health_info() -> dict:
    return {
        "status": "ok" if _cached_forecast is not None else "cold_start",
        "cache_populated": _cached_forecast is not None,
        "last_refit": _last_refit,
        "weeks_history": _weeks_history,
        "last_history_date": _last_history_date.isoformat() if _last_history_date else None,
        "config": PROPHET_CONFIG,
        "best_params": BEST_PARAMS,
    }

from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app.forecast_service import fit_and_cache, get_cached_forecast, get_health_info, BEST_PARAMS
from app.schemas import ForecastRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Demand Forecasting API",
    description="Prophet-based demand forecasting for UK retail sales",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = BackgroundScheduler()
LANDING_PATH = Path(__file__).parent / "templates" / "landing.html"


@app.on_event("startup")
def on_startup():
    logger.info("Starting up and fitting model")
    try:
        fit_and_cache()
    except Exception as exc:
        logger.error(f"Initial fit failed: {exc}")

    scheduler.add_job(fit_and_cache, "cron", hour=0, minute=0, id="fit_and_cache")
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


@app.get("/", response_class=HTMLResponse)
def home():
    if LANDING_PATH.exists():
        return LANDING_PATH.read_text(encoding="utf-8")
    return HTMLResponse("<h1>Demand Forecasting API</h1><p>Service is running</p>")


@app.get("/health")
def health():
    return get_health_info()


@app.post("/forecast")
def forecast(req: ForecastRequest):
    try:
        df_slice = get_cached_forecast(req.horizon_weeks)
        points = [
            {
                "ds": str(row["ds"])[:10],
                "yhat": float(row["yhat"]),
                "yhat_lower": float(row["yhat_lower"]),
                "yhat_upper": float(row["yhat_upper"]),
            }
            for _, row in df_slice.iterrows()
        ]

        return {
            "horizon_weeks": req.horizon_weeks,
            "forecast": points,
            "model_info": {
                "model": "Prophet multiplicative",
                "best_params": BEST_PARAMS,
                "history_weeks": get_health_info()["weeks_history"],
            },
        }

    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Forecast error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error") from exc

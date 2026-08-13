import pytest
from fastapi.testclient import TestClient
import pandas as pd
from app.main import app


@pytest.fixture
def client():
    # Using a context manager triggers FastAPI's startup/shutdown lifespan
    # events (fit_and_cache runs on startup). Without "with", the app never
    # fits a model and /health reports weeks_history == 0.
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["weeks_history"] > 0
    assert data["config"]["weekly_seasonality"] is False

    df = pd.read_csv("data/weekly_sales.csv")
    assert data["weeks_history"] == len(df)


def test_forecast_valid(client):
    response = client.post("/forecast", json={"horizon_weeks": 12})
    assert response.status_code == 200
    assert len(response.json()["forecast"]) == 12


def test_forecast_invalid(client):
    assert client.post("/forecast", json={"horizon_weeks": 0}).status_code == 422
    assert client.post("/forecast", json={"horizon_weeks": 99}).status_code == 422

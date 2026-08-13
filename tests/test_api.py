from fastapi.testclient import TestClient
import pandas as pd
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["weeks_history"] > 0
    assert data["config"]["weekly_seasonality"] is False

    df = pd.read_csv("data/weekly_sales.csv")
    assert data["weeks_history"] == len(df)


def test_forecast_valid():
    response = client.post("/forecast", json={"horizon_weeks": 12})
    assert response.status_code == 200
    assert len(response.json()["forecast"]) == 12


def test_forecast_invalid():
    assert client.post("/forecast", json={"horizon_weeks": 0}).status_code == 422
    assert client.post("/forecast", json={"horizon_weeks": 99}).status_code == 422

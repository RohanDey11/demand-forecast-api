# Demand Forecasting API

Live production API for weekly demand forecasting using Prophet. Trained on 106 weeks of UK Online Retail II data.

**Live Demo:** https://demand-forecast-api-o7u5.onrender.com  
**Docs:** /docs  
**Health:** /health

## Overview

- Model: Prophet multiplicative seasonality with UK holidays
- Data: 106 weeks (2009-12-06 to 2011-12-11), 84 train / 22 test
- Best params: changepoint_prior_scale=0.5, seasonality_prior_scale=10.0
- Performance: Prophet 20.52% MAPE, SARIMA 19.12% RMSE 55,472.02

## Architecture

- FastAPI with scheduled daily refit (APScheduler)
- Cached forecast sliced by horizon for fast response
- Multi-stage Docker build for lean runtime
- Input validation: horizon 1-22 weeks, 422 on invalid

## Project Structure

```
├── app/
│   ├── main.py
│   ├── forecast_service.py
│   ├── schemas.py
│   └── templates/landing.html
├── data/
│   └── weekly_sales.csv
├── tests/
├── Dockerfile
└── requirements.txt
```

## Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deployment

Render:
```bash
docker build -t demand-forecast-api .
docker run -p 8000:8000 demand-forecast-api
```

Environment variable `PORT` is respected.

## API

**POST /forecast**
```json
{
  "horizon_weeks": 12
}
```

Response includes `ds`, `yhat`, `yhat_lower`, `yhat_upper`.

**GET /health**
Returns cache status, last refit timestamp, history size.

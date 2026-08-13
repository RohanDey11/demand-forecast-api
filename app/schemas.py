from pydantic import BaseModel, Field
from typing import List


class ForecastRequest(BaseModel):
    horizon_weeks: int = Field(..., ge=1, le=22, description="Forecast horizon in weeks")


class ForecastPoint(BaseModel):
    ds: str
    yhat: float
    yhat_lower: float
    yhat_upper: float


class ForecastResponse(BaseModel):
    horizon_weeks: int
    forecast: List[ForecastPoint]
    model_info: dict

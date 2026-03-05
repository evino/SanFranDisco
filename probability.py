import sqlite3

from db import DB_PATH, get_forecast_actuals


def probability_reached(forecast_actuals: list[tuple[float, float]], threshold: float) -> dict:
    """
    Given (forecast_high, actual_high) pairs and a threshold temp,
    return P(actual >= threshold).
    """
    if not forecast_actuals:
        return {"threshold": threshold, "samples": 0, "probability": None}

    reached = sum(1 for _, actual in forecast_actuals if actual == threshold)
    return {
        "threshold": threshold,
        "samples": len(forecast_actuals),
        "probability": round(reached / len(forecast_actuals), 3),
    }


def get_probability(predicted_temp: float, days_ahead: int = 1) -> dict:
    """
    Open the DB, fetch historical forecast/actual pairs where GFS forecast
    exactly matched predicted_temp, and return P(actual >= predicted_temp).
    """
    with sqlite3.connect(DB_PATH) as conn:
        pairs = get_forecast_actuals(conn, predicted_temp, days_ahead)
    return probability_reached(pairs, predicted_temp)

import sqlite3
from collections import Counter

from db import DB_PATH, get_forecast_actuals


def build_distribution(forecast_actuals: list[tuple[float, float]]) -> dict:
    """
    Given (forecast_high, actual_high) pairs, return a distribution of actual outcomes.
    """
    if not forecast_actuals:
        return {"samples": 0, "distribution": {}}

    actuals = [round(actual) for _, actual in forecast_actuals]
    counts = Counter(actuals)
    n = len(actuals)
    distribution = {temp: round(count / n, 4) for temp, count in sorted(counts.items())}

    return {"samples": n, "distribution": distribution}


def get_probability(predicted_temp: float, days_ahead: int = 1) -> dict:
    """
    Open the DB, fetch historical forecast/actual pairs where GFS forecast
    exactly matched predicted_temp, and return a distribution of actual outcomes.
    """
    with sqlite3.connect(DB_PATH) as conn:
        pairs = get_forecast_actuals(conn, predicted_temp, days_ahead)
    return build_distribution(pairs)

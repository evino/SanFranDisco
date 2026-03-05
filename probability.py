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


def GetTempProbability(predicted_temp: float, days_ahead: int = 1) -> dict:
    """
    Open the DB, fetch historical forecast/actual pairs where GFS forecast
    exactly matched predicted_temp, and return a distribution of actual outcomes.
    """
    with sqlite3.connect(DB_PATH) as conn:
        pairs = get_forecast_actuals(conn, predicted_temp, days_ahead)
    return build_distribution(pairs)

# Return probability of each bracket
def GetBracketProbability(predicted_temp: float, brackets: list, days_ahead: int = 1) -> dict:
    result = GetTempProbability(predicted_temp, days_ahead)
    distribution = result["distribution"]

    bucketed = {}
    for bracket in brackets:
        if bracket[0] == '<':
            label = f"< {bracket[1]}"
            prob = sum(p for temp, p in distribution.items() if temp < bracket[1])
        elif bracket[0] == '>':
            label = f"> {bracket[1]}"
            prob = sum(p for temp, p in distribution.items() if temp > bracket[1])
        else:
            low, high = bracket
            label = f"{low}-{high}"
            prob = sum(p for temp, p in distribution.items() if low <= temp <= high)
        bucketed[label] = round(prob, 4)

    return {"samples": result["samples"], "distribution": bucketed}

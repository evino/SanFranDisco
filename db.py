import sqlite3
import csv
import io
from collections import defaultdict
from datetime import date, timedelta
import requests

DB_PATH = "data/high_temps.db"


def build_url() -> str:
    today = date.today()
    start = today - timedelta(days=365 * 2)
    return (
        "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
        f"?station=SFO&data=tmpf"
        f"&year1={start.year}&month1={start.month}&day1={start.day}"
        f"&year2={today.year}&month2={today.month}&day2={today.day}"
        "&format=onlycomma&tz=America/Los_Angeles"
    )


def fetch_daily_highs(url: str) -> dict[str, float]:
    """Fetch CSV and return {date_str: high_temp_f} for each day."""
    response = requests.get(url)
    response.raise_for_status()

    daily_temps: dict[str, list[float]] = defaultdict(list)
    reader = csv.DictReader(io.StringIO(response.text))
    for row in reader:
        tmpf = row["tmpf"].strip()
        if tmpf == "M":
            continue
        date = row["valid"].strip()[:10]  # "YYYY-MM-DD"
        daily_temps[date].append(float(tmpf))

    return {date: max(temps) for date, temps in daily_temps.items()}


def build_forecast_url() -> str:
    today = date.today()
    start = today - timedelta(days=365 * 2)
    return (
        "https://mesonet.agron.iastate.edu/cgi-bin/request/mos.py"
        f"?station=KSFO&model=GFS"
        f"&year1={start.year}&month1={start.month}&day1={start.day}&hour1=0"
        f"&year2={today.year}&month2={today.month}&day2={today.day}&hour2=0"
    )


def fetch_forecast_highs(url: str) -> list[tuple[str, str, float]]:
    """Fetch MOS CSV and return (runtime, forecast_date, high_temp_f) rows."""
    response = requests.get(url)
    response.raise_for_status()

    # Group by (runtime, forecast_date) -> list of temps
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    reader = csv.DictReader(io.StringIO(response.text))
    for row in reader:
        tmp = row["tmp"].strip()
        if not tmp:
            continue
        runtime = row["runtime"].strip()[:16]       # "YYYY-MM-DD HH:MM"
        forecast_date = row["ftime"].strip()[:10]   # "YYYY-MM-DD"
        groups[(runtime, forecast_date)].append(float(tmp))

    return [(rt, fd, max(temps)) for (rt, fd), temps in groups.items()]


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS high_temps (
            date TEXT PRIMARY KEY,
            high_temp_f REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            runtime TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            high_temp_f REAL NOT NULL,
            PRIMARY KEY (runtime, forecast_date)
        )
    """)
    conn.commit()


def upsert_highs(conn: sqlite3.Connection, daily_highs: dict[str, float]) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO high_temps (date, high_temp_f) VALUES (?, ?)",
        daily_highs.items(),
    )
    conn.commit()


def upsert_forecasts(conn: sqlite3.Connection, rows: list[tuple[str, str, float]]) -> None:
    conn.executemany(
        "INSERT OR REPLACE INTO forecasts (runtime, forecast_date, high_temp_f) VALUES (?, ?, ?)",
        rows,
    )
    conn.commit()


def get_forecast_actuals(
    conn: sqlite3.Connection,
    predicted_temp: float,
    days_ahead: int = 1,
) -> list[tuple[float, float]]:
    """
    Return (forecast_high, actual_high) pairs from history where the GFS forecast
    exactly matched `predicted_temp` and was made `days_ahead` days in advance.
    """
    return conn.execute("""
        SELECT f.high_temp_f, h.high_temp_f
        FROM forecasts f
        JOIN high_temps h ON f.forecast_date = h.date
        WHERE f.high_temp_f = ?
          AND CAST(julianday(f.forecast_date) - julianday(date(f.runtime)) AS INTEGER) = ?
    """, (predicted_temp, days_ahead)).fetchall()


def main():
    print("Fetching observed temperature data...")
    daily_highs = fetch_daily_highs(build_url())
    print(f"Found {len(daily_highs)} days of observed data")

    print("Fetching forecast data...")
    forecast_rows = fetch_forecast_highs(build_forecast_url())
    print(f"Found {len(forecast_rows)} (runtime, date) forecast rows")

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)
        upsert_highs(conn, daily_highs)
        upsert_forecasts(conn, forecast_rows)

    print(f"Saved to {DB_PATH}")


if __name__ == "__main__":
    main()

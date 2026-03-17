import requests
import json
import csv
import io

from datetime import datetime, timezone, timedelta, time, date


noaa_url = "https://api.weather.gov/gridpoints/MTR/85,98/forecast/hourly"


# Get NWS metadata
def GetWeatherData(url) -> dict:
    data = requests.get(url).json()
    # print(json.dumps(data, indent=4))
    return data

# Returns number of hours left in current day
def HoursLeftInDay(dt=None):
    if dt is None:
        dt = datetime.now()
    current_hour = dt.replace(minute=0, second=0, microsecond=0)
    midnight = (current_hour + timedelta(days=1)).replace(hour=0)
    return int((midnight - current_hour).total_seconds() // 3600)

"""
Returns highest temperature for a 24-hour window based off a start period
"""
def GetHighTemp(WeatherData, startPeriod=0) -> int:
    startPeriod += 1
    endPeriod = startPeriod + 24

    # Grab each period for 24 hour window based off startPeriod
    periods = WeatherData["properties"]["periods"][startPeriod:endPeriod]
    high_temp = max(int(p["temperature"]) for p in periods)


    # For Debug
    #print(f"NWS-predicted high temp tomorrow ({periods[0]["startTime"]}) is: {high_temp}")

    return high_temp


def GetGFSMOSHigh(days_ahead: int = 1) -> float | None:
    """
    Fetch the latest GFS MOS n_x (daily high) for KSFO `days_ahead` days from today.
    Returns the high temp in °F, or None if unavailable.
    """
    today = date.today()
    target = today + timedelta(days=days_ahead)
    target_str = target.strftime("%Y-%m-%d")

    url = (
        "https://mesonet.agron.iastate.edu/cgi-bin/request/mos.py"
        f"?station=KSFO&model=GFS"
        f"&year1={today.year}&month1={today.month}&day1={today.day}&hour1=0"
        f"&year2={today.year}&month2={today.month}&day2={today.day}&hour2=23"
    )
    response = requests.get(url)
    response.raise_for_status()

    # Find the most recent runtime's n_x for the target date midnight row
    best_runtime, best_high = None, None
    reader = csv.DictReader(io.StringIO(response.text))
    for row in reader:
        if not row["n_x"].strip() or row["ftime"].strip()[:10] != target_str:
            continue
        runtime = row["runtime"].strip()
        n_x = float(row["n_x"].strip())
        if best_runtime is None or runtime > best_runtime:
            best_runtime, best_high = runtime, n_x

    return best_high


def main():
    from probability import GetTempProbability

    noaa_data = GetWeatherData(noaa_url)
    print(json.dumps(noaa_data, indent=4))
    startPeriod = HoursLeftInDay()
    predicted = GetHighTemp(noaa_data, startPeriod)

    result = GetTempProbability(predicted)
    if not result["samples"]:
        print("Not enough historical data for this temperature range.")
    else:
        print(f"Actual outcome distribution when GFS forecast {predicted}°F ({result['samples']} samples):")
        for temp, prob in result["distribution"].items():
            print(f"  {temp}°F: {prob:.1%}")




if __name__ == "__main__":
    main()

import requests
import json

from datetime import datetime, timezone, timedelta, time


noaa_url = "https://api.weather.gov/gridpoints/MTR/85,98/forecast/hourly"
tz = timezone(timedelta(hours=-8))
dt = datetime.now(tz)


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
def GetTemps(WeatherData, startPeriod=0) -> float:
    startPeriod += 1
    endPeriod = startPeriod + 24

    # Grab each period for 24 hour window based off startPeriod
    periods = WeatherData["properties"]["periods"][startPeriod:endPeriod]
    high_temp = max(float(p["temperature"]) for p in periods)


    # For debug
    # print(json.dumps(periods, indent=4))
    # for p in periods:
    #     print(p["temperature"])

    print(f"High temp tomorrow ({periods[0]["startTime"]}) is: {high_temp}")
    # print(json.dumps(periods[0]["temperature"], indent=4))

    return high_temp


def main():
    noaa_data = GetWeatherData(noaa_url)
    # print(json.dumps(noaa_data, indent=4))

    startPeriod = HoursLeftInDay()
    GetTemps(noaa_data, startPeriod)

    now = dt  # Current date
    tomorrow = now.date() + timedelta(days=1)
    start = datetime.combine(tomorrow, time.min, tzinfo=tz).isoformat()
    end = datetime.combine(tomorrow + timedelta(days=1), time.min, tzinfo=tz).isoformat()
    
        
    # print(start)
    # print(end)

    # DateFilter()

if __name__ == "__main__":
    main()

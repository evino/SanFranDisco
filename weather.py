import requests
import json

from datetime import datetime, timezone, timedelta, time


noaa_url = "https://api.weather.gov/gridpoints/MTR/85,98/forecast/hourly"
tz = timezone(timedelta(hours=-8))
dt = datetime.now(tz)

def GetWeatherData(url) -> dict:
    data = requests.get(url).json()
    # print(json.dumps(data, indent=4))
    return data

def DateFilter(StartDate, EndDate):
    print(date)

def GetTemps(WeatherData):
    periods = WeatherData["properties"]["periods"]
    high_temp = max(p["temperature"] for p in periods)
    for p in periods:
        print(p["temperature"])

    print(f"High temp of the day is: {high_temp}")
    # print(json.dumps(periods[0]["temperature"], indent=4))

def main():
    noaa_data = GetWeatherData(noaa_url)
    GetTemps(noaa_data)

    now = dt  # Current date
    tomorrow = now.date() + timedelta(days=1)
    start = datetime.combine(tomorrow, time.min, tzinfo=tz).isoformat()
    end = datetime.combine(tomorrow + timedelta(days=1), time.min, tzinfo=tz).isoformat()
    print(start)
    print(end)

    # DateFilter()

if __name__ == "__main__":
    main()

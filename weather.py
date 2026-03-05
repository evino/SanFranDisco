import requests
import json

from datetime import datetime, timezone, timedelta, time


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


def main():
    from probability import GetTempProbability

    noaa_data = GetWeatherData(noaa_url)
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

# Entry point file

from series import GetBrackets
from weather import GetWeatherData, GetHighTemp, HoursLeftInDay
from probability import GetTempProbability, GetBracketProbability

def main():
    noaa_url = "https://api.weather.gov/gridpoints/MTR/85,98/forecast/hourly"
    startPeriod = HoursLeftInDay()
    noaa_data = GetWeatherData(noaa_url)
    predictedHighTemp = GetHighTemp(noaa_data, startPeriod)

    print(f"NWS-predicted high temp tomorrow is: {predictedHighTemp}\n")

    probabilities = GetTempProbability(predictedHighTemp)
    if not probabilities["samples"]:
        print("Not enough historical data for this temperature range.")
    else:
        print(f"Actual outcome distribution when GFS forecast {predictedHighTemp}°F ({probabilities['samples']} samples):")
        for temp, prob in probabilities["distribution"].items():
            print(f"  {temp}°F: {prob:.1%}")

    print(f"\nTomorrows brackets: {GetBrackets()}")
    bracket_probs = GetBracketProbability(predictedHighTemp, GetBrackets())
    print(f"Bracket probabilities ({bracket_probs['samples']} samples):")
    for label, prob in bracket_probs["distribution"].items():
        print(f"  {label}°F: {prob:.1%}")



if __name__ == "__main__":
    main()
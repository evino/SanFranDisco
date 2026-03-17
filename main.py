# Entry point file

from series import GetBrackets
from weather import GetWeatherData, GetHighTemp, HoursLeftInDay, GetGFSMOSHigh
from probability import GetTempProbability, GetBracketProbability


CHECK_BRACKETS = False

def print_forecast(label: str, predicted_high: float | None):
    if predicted_high is None:
        print(f"{label}: unavailable\n")
        return
    print(f"{label} predicted high tomorrow: {predicted_high}°F")
    probabilities = GetTempProbability(predicted_high)
    if not probabilities["samples"]:
        print("  Not enough historical data for this temperature range.")
    else:
        print(f"  Actual outcome distribution ({probabilities['samples']} samples):")
        for temp, prob in probabilities["distribution"].items():
            print(f"    {temp}°F: {prob:.1%}")
    print()

def main():
    noaa_url = "https://api.weather.gov/gridpoints/MTR/85,98/forecast/hourly"
    startPeriod = HoursLeftInDay()
    noaa_data = GetWeatherData(noaa_url)
    nwsHigh = GetHighTemp(noaa_data, startPeriod)
    mosHigh = GetGFSMOSHigh()

    print_forecast("NWS Hourly", nwsHigh)
    print_forecast("GFS MOS", mosHigh)

    if not CHECK_BRACKETS:
        return

    print(f"\nTomorrows brackets: {GetBrackets()}")
    bracket_probs = GetBracketProbability(predictedHighTemp, GetBrackets())
    print(f"Bracket probabilities ({bracket_probs['samples']} samples):")
    for label, prob in bracket_probs["distribution"].items():
        print(f"  {label}°F: {prob:.1%}")



if __name__ == "__main__":
    main()
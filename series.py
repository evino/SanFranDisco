import requests
import json
from datetime import date, timedelta

# Get series information
tomorrow = date.today() + timedelta(days=1)
date_str = tomorrow.strftime("%y%b%d").upper()
url = f"https://api.elections.kalshi.com/trade-api/v2/events/KXHIGHTSFO-{date_str}"
response = requests.get(url)
series_data = response.json()


# Get brackets/markets for climate predition. Returns a list of tuples for different brackets.
def GetBrackets():
    marketsData = requests.get(url).json()["markets"]
    # print(marketsData)

    brackets = []
    
    brackets.append(("<", marketsData[0]["cap_strike"]))
    for market in marketsData[1:5]:
        brackets.append((market["floor_strike"], market["cap_strike"]))
    brackets.append((">", marketsData[5]["floor_strike"]))

    return brackets


def main():
    # print(json.dumps(series_data, indent=4))
    print(GetBrackets())

if __name__ == "__main__":
    main()
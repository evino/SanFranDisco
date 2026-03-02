import requests
import json

# Get series information
url = "https://api.elections.kalshi.com/trade-api/v2/events/KXHIGHTSFO-26MAR02"
response = requests.get(url)
series_data = response.json()

print(json.dumps(series_data, indent=4))

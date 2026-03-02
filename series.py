import requests
import json

# Get series information
url = "https://api.elections.kalshi.com/trade-api/v2/series/KXHIGHTSFO"
response = requests.get(url)
series_data = response.json()

print(json.dumps(series_data, indent=4))

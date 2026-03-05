import requests
import json
from datetime import date, timedelta

# Get series information
tomorrow = date.today() + timedelta(days=1)
date_str = tomorrow.strftime("%y%b%d").upper()
url = f"https://api.elections.kalshi.com/trade-api/v2/events/KXHIGHTSFO-{date_str}"
response = requests.get(url)
series_data = response.json()

print(json.dumps(series_data, indent=4))

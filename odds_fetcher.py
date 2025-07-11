import requests
import os
from datetime import datetime

API_KEY = "2b95710869f3dbdb2a939bac365e9ce1"
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer/odds"

def get_today_matches():
    params = {
        "apiKey": API_KEY,
        "regions": "eu",  # Focus on European markets
        "markets": "h2h",  # Head-to-head (1X2)
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "bookmakers": "efbet,betano,winbet"  # ✅ Filter only Bulgarian bookmakers
    }

    response = requests.get(BASE_URL, params=params)
    
        print("🔍 Raw Odds API Response:")
        print(response.json())

    if response.status_code != 200:
        raise Exception(f"Failed to fetch odds: {response.status_code} — {response.text}")

    data = response.json()
    today_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Filter matches to include only today's games with available odds
    today_matches = []
    for match in data:
        match_time = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
        if match_time.strftime("%Y-%m-%d") == today_str and match.get("bookmakers"):
            today_matches.append(match)

    return today_matches

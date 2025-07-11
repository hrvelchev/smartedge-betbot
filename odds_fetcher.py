# odds_fetcher.py

import requests
from datetime import datetime
import pytz

API_KEY = "2b95710869f3dbdb2a939bac365e9ce1"
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer/odds"

def get_today_matches():
    tz_sofia = pytz.timezone("Europe/Sofia")
    now = datetime.now(tz_sofia)
    today_str = now.strftime("%Y-%m-%d")

    params = {
        "apiKey": API_KEY,
        "regions": "eu",               # EU bookmakers (Betano, efbet, bwin, etc.)
        "markets": "h2h",              # Head-to-head (1X2)
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        matches_today = []

        for event in data:
            if "commence_time" not in event:
                continue

            match_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00")).astimezone(tz_sofia)
            if match_time.strftime("%Y-%m-%d") != today_str:
                continue

            bookmakers = event.get("bookmakers", [])
            if not bookmakers:
                continue

            best_bookmaker = bookmakers[0]
            odds = best_bookmaker.get("markets", [])[0]["outcomes"]
            match = {
                "home_team": event["home_team"],
                "away_team": event["away_team"],
                "start_time": match_time.strftime("%H:%M"),
                "bookmaker": best_bookmaker["title"],
                "odds": {o["name"]: o["price"] for o in odds}
            }

            matches_today.append(match)

        return matches_today

    except Exception as e:
        print(f"Error fetching odds: {e}")
        return []

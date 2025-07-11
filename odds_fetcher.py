import requests
import os
from datetime import datetime, timedelta

API_KEY = "2b95710869f3dbdb2a939bac365e9ce1"
BASE_URL = "https://api.the-odds-api.com/v4/sports/soccer/odds"

def fetch_matches():
    params = {
        "apiKey": API_KEY,
        "regions": "eu",  # Focus on European markets
        "markets": "h2h",  # Head-to-head (1X2)
        "oddsFormat": "decimal",
        "dateFormat": "iso",
        "bookmakers": "efbet,betano,winbet"
    }

    response = requests.get(BASE_URL, params=params)

    print("📡 API Status Code:", response.status_code)
    try:
        data = response.json()
        print(f"🔎 Received {len(data)} matches.")
        for match in data[:3]:  # Show only first 3 matches
            print("⚽ Match preview:", match)
    except Exception as e:
        print("❌ Error parsing JSON:", e)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch odds: {response.status_code} — {response.text}")

    return response.json()

def get_today_matches():
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    return filter_matches_by_date(today_str)

def get_tomorrow_matches():
    tomorrow_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    return filter_matches_by_date(tomorrow_str)

def filter_matches_by_date(date_str):
    all_matches = fetch_matches()
    filtered = []

    for match in all_matches:
        match_date = match["commence_time"][:10]

        # Ensure match has valid bookmaker and market data
        if (
            match_date == date_str and
            match.get("bookmakers") and
            match["bookmakers"][0].get("markets")
        ):
            filtered.append(match)

    return filtered

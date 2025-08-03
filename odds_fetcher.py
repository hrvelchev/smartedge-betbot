"""
Odds fetching utilities for SmartEdgeBetBot.

This module interfaces with The Odds API to retrieve soccer matches and their
associated odds.  The original implementation used a hard‑coded sport key
(`soccer`) and passed unsupported bookmaker values directly in the API call.
However, The Odds API requires specific sport keys (e.g. ``soccer_epl``) and
only certain bookmakers are supported.  In addition, the API key and other
configuration are provided via environment variables.

The revised implementation below dynamically discovers active soccer sports,
fetches odds for each sport, and filters events by date using the user's
timezone (Europe/Sofia).  It also avoids specifying unsupported bookmakers in
the API request – bookmaker filtering happens client‑side via ``tip_generator``.
"""

import os
from datetime import datetime, timedelta
from typing import List

import pytz
import requests

# The Odds API key.  It is strongly recommended to set ODDS_API_KEY in the
# deployment environment.  A fallback key is provided for local testing but
# may be rate‑limited or inactive.
API_KEY = os.getenv("ODDS_API_KEY", "2b95710869f3dbdb2a939bac365e9ce1")

# Base endpoints for The Odds API.  ``SPORTS_URL`` returns a list of sports,
# while ``ODDS_URL_TEMPLATE`` is used to retrieve odds for a specific sport
# key.  See https://the-odds-api.com/liveapi/guides/v4/ for details.
SPORTS_URL = "https://api.the-odds-api.com/v4/sports"
ODDS_URL_TEMPLATE = "https://api.the-odds-api.com/v4/sports/{sport_key}/odds"

# Timezone used for determining today/tomorrow.  Using Europe/Sofia ensures
# that date boundaries align with the bot's intended locale.
SOFIA_TZ = pytz.timezone("Europe/Sofia")

def get_active_soccer_keys() -> List[str]:
    """Return a list of active sport keys belonging to the Soccer group.

    The Odds API lists many sport keys (e.g. ``soccer_epl``, ``soccer_la_liga``).
    This helper fetches the sports endpoint and filters for those where
    ``group`` is ``"Soccer"`` and the sport is currently active.  If the API
    request fails, an empty list is returned.
    """
    try:
        resp = requests.get(
            SPORTS_URL,
            params={"apiKey": API_KEY},
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"❌ Failed to fetch sports list: {resp.status_code} – {resp.text}")
            return []
        sports = resp.json()
        soccer_keys = [s.get("key") for s in sports if s.get("group") == "Soccer" and s.get("active")]
        return soccer_keys
    except Exception as e:
        print(f"❌ Exception retrieving sports list: {e}")
        return []


def fetch_matches() -> List[dict]:
    """Fetch upcoming soccer matches with odds from The Odds API.

    This function iterates over all active soccer sport keys and retrieves
    head‑to‑head odds for European bookmakers.  It does not specify the
    ``bookmakers`` parameter – by omitting unsupported bookmakers from the
    request we receive a broader set of matches.  Bookmaker filtering will
    happen in ``tip_generator.py``.

    Returns a list of match dictionaries as returned by The Odds API.
    """
    params_common = {
        "apiKey": API_KEY,
        "regions": "eu",  # Focus on European markets
        "markets": "h2h",  # Head-to-head (1X2)
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }

    all_matches: List[dict] = []
    sport_keys = get_active_soccer_keys()
    if not sport_keys:
        print("⚠️ No active soccer sports found via The Odds API.")
    for sport_key in sport_keys:
        url = ODDS_URL_TEMPLATE.format(sport_key=sport_key)
        try:
            response = requests.get(url, params=params_common, timeout=10)
            print(f"📡 Fetching odds for {sport_key}: status {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Failed to fetch odds for {sport_key}: {response.text}")
                continue
            data = response.json()
            print(f"🔎 {sport_key} returned {len(data)} events")
            all_matches.extend(data)
        except Exception as e:
            print(f"❌ Exception fetching odds for {sport_key}: {e}")
    return all_matches


def get_today_matches() -> List[dict]:
    """Return a list of matches commencing today in the Sofia timezone."""
    today_str = datetime.now(SOFIA_TZ).strftime("%Y-%m-%d")
    return filter_matches_by_date(today_str)


def get_tomorrow_matches() -> List[dict]:
    """Return a list of matches commencing tomorrow in the Sofia timezone."""
    tomorrow_str = (datetime.now(SOFIA_TZ) + timedelta(days=1)).strftime("%Y-%m-%d")
    return filter_matches_by_date(tomorrow_str)


def filter_matches_by_date(date_str: str) -> List[dict]:
    """Filter all fetched matches by the given ISO date string.

    A match is kept if its ``commence_time`` date matches ``date_str`` and
    **any** bookmaker provides at least one market.  This is more inclusive
    than the original implementation, which only considered the first bookmaker.
    """
    all_matches = fetch_matches()
    filtered: List[dict] = []
    for match in all_matches:
        # Extract the date component (YYYY-MM-DD) from the ISO timestamp
        match_date = match.get("commence_time", "")[:10]
        if match_date != date_str:
            continue
        # Ensure at least one bookmaker has markets
        bookmakers = match.get("bookmakers") or []
        has_markets = any(b.get("markets") for b in bookmakers)
        if has_markets:
            filtered.append(match)
    return filtered
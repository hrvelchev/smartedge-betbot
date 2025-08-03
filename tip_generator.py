"""
Tip generation module for SmartEdgeBetBot.

This module retrieves today's or tomorrow's soccer matches via the
``odds_fetcher`` module, applies a predictive model to calculate expected
value (EV) for each possible outcome, and returns a formatted list of
betting tips.  The code has been updated to:

* Iterate through **all** bookmakers for each match to find one of the
  preferred bookmakers (Pinnacle, Betfair or Unibet).  
* Use the new ``odds_fetcher`` implementation that dynamically gathers
  active soccer sports and filters matches in the Sofia timezone.
* Maintain the EV/odds filtering logic for high‑value tips.
"""

from datetime import datetime, timedelta
from typing import List, Dict

from odds_fetcher import get_today_matches
from model import load_model_and_predict

# Preferred bookmakers (case-insensitive)
PREFERRED_BOOKMAKERS = {"pinnacle", "betfair", "unibet"}

def filter_tips(tips: List[Dict]) -> List[Dict]:
    """Apply bookmaker, odds and EV filters to a list of raw tip dicts.

    A tip is kept if its odds lie between 1.85 and 3.50 (inclusive), its
    expected value (EV) is at least 5%, and the bookmaker name is one of
    Pinnacle, Betfair or Unibet (case‑insensitive).
    """
    print(f"📦 Filtering {len(tips)} raw tips...")
    allowed = {b.lower() for b in PREFERRED_BOOKMAKERS}
    filtered = [
        t
        for t in tips
        if 1.85 <= t["odds"] <= 3.50
        and t["ev"] >= 5
        and t["bookie"].lower() in allowed
    ]
    print(f"✅ Tips after filtering: {len(filtered)}")
    return filtered


def generate_daily_tips() -> str:
    """Generate tips for matches taking place today."""
    print("📅 Generating tips for TODAY...")
    matches = get_today_matches()
    print(f"🔍 Matches fetched: {len(matches)}")
    if not matches:
        return "⚠️ No matches found for today from selected bookmakers."

    model = load_model_and_predict()
    print("🧠 Prediction model loaded.")
    raw_tips: List[Dict] = []
    today_str = matches[0]["commence_time"][:10]
    allowed = {b.lower() for b in PREFERRED_BOOKMAKERS}

    for match in matches:
        try:
            home = match["home_team"]
            away = match["away_team"]
            match_time = match["commence_time"][11:16]
            selected_bookmaker = None
            for bookmaker in match.get("bookmakers", []):
                if (
                    bookmaker.get("markets")
                    and bookmaker.get("title", "").lower() in allowed
                ):
                    selected_bookmaker = bookmaker
                    break
            if not selected_bookmaker:
                continue
            bookie = selected_bookmaker["title"]
            outcomes = selected_bookmaker["markets"][0]["outcomes"]

            print(f"\n➡️ Analyzing: {home} vs {away} @ {match_time} ({bookie})")

            for outcome in outcomes:
                team = outcome["name"]
                odds = outcome["price"]
                implied_prob = 1 / odds
                model_prob = model.predict_proba([[home, away, team]])[0][1]
                ev = (odds * model_prob - 1) * 100
                print(f"📊 {team}: odds={odds}, model_prob={model_prob:.4f}, EV={ev:.2f}")
                raw_tips.append({
                    "match": f"{home} vs {away}",
                    "tip": team,
                    "odds": round(odds, 2),
                    "ev": round(ev, 2),
                    "bookie": bookie,
                    "time": match_time,
                    "date": match["commence_time"][:10],
                })
        except Exception as e:
            print(f"❌ Error analyzing match: {e}")

    filtered_tips = [t for t in filter_tips(raw_tips) if t["date"] == today_str]
    if not filtered_tips:
        return "⚠️ No high-value tips found today within odds range 1.85–3.50 from selected bookmakers."

    message = f"🎯 AI-Generated Tips for {today_str}:\n"
    for tip in filtered_tips:
        message += (
            f"\n🏟️ {tip['match']} @ {tip['time']}"
            f"\n📊 Tip: {tip['tip']} @ {tip['odds']} (Bookie: {tip['bookie']})"
            f"\n✅ EV: {tip['ev']}%\n"
        )
    print("✅ Finished generating today’s tips.")
    return message


def generate_tomorrow_tips() -> str:
    """Generate tips for matches taking place tomorrow."""
    print("📅 Generating tips for TOMORROW...")
    from odds_fetcher import get_tomorrow_matches
    matches = get_tomorrow_matches()
    print(f"🔍 Matches fetched: {len(matches)}")
    if not matches:
        return "⚠️ No matches found for tomorrow from selected bookmakers."

    model = load_model_and_predict()
    print("🧠 Prediction model loaded.")
    raw_tips: List[Dict] = []
    tomorrow_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    allowed = {b.lower() for b in PREFERRED_BOOKMAKERS}

    for match in matches:
        try:
            home = match["home_team"]
            away = match["away_team"]
            match_time = match["commence_time"][11:16]
            selected_bookmaker = None
            for bookmaker in match.get("bookmakers", []):
                if (
                    bookmaker.get("markets")
                    and bookmaker.get("title", "").lower() in allowed
                ):
                    selected_bookmaker = bookmaker
                    break
            if not selected_bookmaker:
                continue
            bookie = selected_bookmaker["title"]
            outcomes = selected_bookmaker["markets"][0]["outcomes"]

            print(f"\n➡️ Analyzing: {home} vs {away} @ {match_time} ({bookie})")

            for outcome in outcomes:
                team = outcome["name"]
                odds = outcome["price"]
                implied_prob = 1 / odds
                model_prob = model.predict_proba([[home, away, team]])[0][1]
                ev = (odds * model_prob - 1) * 100
                print(f"📊 {team}: odds={odds}, model_prob={model_prob:.4f}, EV={ev:.2f}")
                raw_tips.append({
                    "match": f"{home} vs {away}",
                    "tip": team,
                    "odds": round(odds, 2),
                    "ev": round(ev, 2),
                    "bookie": bookie,
                    "time": match_time,
                    "date": match["commence_time"][:10],
                })
        except Exception as e:
            print(f"❌ Error analyzing match: {e}")

    filtered_tips = [t for t in filter_tips(raw_tips) if t["date"] == tomorrow_str]
    if not filtered_tips:
        return f"⚠️ No high-value tips found for {tomorrow_str} within odds range 1.85–3.50 from selected bookmakers."

    message = f"🎯 AI-Generated Tips for {tomorrow_str}:\n"
    for tip in filtered_tips:
        message += (
            f"\n🏟️ {tip['match']} @ {tip['time']}"
            f"\n📊 Tip: {tip['tip']} @ {tip['odds']} (Bookie: {tip['bookie']})"
            f"\n✅ EV: {tip['ev']}%\n"
        )
    print("✅ Finished generating tomorrow’s tips.")
    return message

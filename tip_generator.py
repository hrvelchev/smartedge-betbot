from odds_fetcher import get_today_matches
from model import load_model_and_predict
from datetime import datetime, timedelta

# Shared filtering logic
def filter_tips(tips):
    return [
        t for t in tips
        if 1.85 <= t['odds'] <= 3.50
        and t['ev'] >= 5
        and t['bookie'].lower() in {"efbet", "betano", "winbet"}
    ]

# ➤ Function to generate today's tips
def generate_daily_tips():
    matches = get_today_matches()
    if not matches:
        return "⚠️ No matches found for today from selected bookmakers."

    model = load_model_and_predict()
    raw_tips = []
    today_str = matches[0]["commence_time"][:10]

    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        match_time = match["commence_time"][11:16]
        bookie = match["bookmakers"][0]["title"]
        outcomes = match["bookmakers"][0]["markets"][0]["outcomes"]

        for outcome in outcomes:
            team = outcome["name"]
            odds = outcome["price"]

            implied_prob = 1 / odds
            model_prob = model.predict_proba([[home, away, team]])[0][1]
            ev = (odds * model_prob - 1) * 100

            raw_tips.append({
                "match": f"{home} vs {away}",
                "tip": team,
                "odds": round(odds, 2),
                "ev": round(ev, 2),
                "bookie": bookie,
                "time": match_time,
                "date": match["commence_time"][:10]
            })

    filtered_tips = [t for t in filter_tips(raw_tips) if t['date'] == today_str]
    if not filtered_tips:
        return "⚠️ No high-value tips found today within odds range 1.85–3.50 from selected bookmakers."

    message = f"🎯 AI-Generated Tips for {today_str}:\n"
    for tip in filtered_tips:
        message += (
            f"\n🏟️ {tip['match']} @ {tip['time']}"
            f"\n📊 Tip: {tip['tip']} @ {tip['odds']} (Bookie: {tip['bookie']})"
            f"\n✅ EV: {tip['ev']}%\n"
        )

    return message

# ➤ Function to generate tomorrow's tips
def generate_tomorrow_tips():
    matches = get_today_matches()
    if not matches:
        return "⚠️ No matches found for tomorrow from selected bookmakers."

    model = load_model_and_predict()
    raw_tips = []
    tomorrow_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

    for match in matches:
        home = match["home_team"]
        away = match["away_team"]
        match_time = match["commence_time"][11:16]
        bookie = match["bookmakers"][0]["title"]
        outcomes = match["bookmakers"][0]["markets"][0]["outcomes"]
        match_date = match["commence_time"][:10]

        for outcome in outcomes:
            team = outcome["name"]
            odds = outcome["price"]

            implied_prob = 1 / odds
            model_prob = model.predict_proba([[home, away, team]])[0][1]
            ev = (odds * model_prob - 1) * 100

            raw_tips.append({
                "match": f"{home} vs {away}",
                "tip": team,
                "odds": round(odds, 2),
                "ev": round(ev, 2),
                "bookie": bookie,
                "time": match_time,
                "date": match_date
            })

    filtered_tips = [t for t in filter_tips(raw_tips) if t['date'] == tomorrow_str]
    if not filtered_tips:
        return f"⚠️ No high-value tips found for {tomorrow_str} within odds range 1.85–3.50 from selected bookmakers."

    message = f"🎯 AI-Generated Tips for {tomorrow_str}:\n"
    for tip in filtered_tips:
        message += (
            f"\n🏟️ {tip['match']} @ {tip['time']}"
            f"\n📊 Tip: {tip['tip']} @ {tip['odds']} (Bookie: {tip['bookie']})"
            f"\n✅ EV: {tip['ev']}%\n"
        )

    return message

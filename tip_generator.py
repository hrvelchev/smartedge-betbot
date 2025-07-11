from odds_fetcher import get_today_matches
from model import load_model_and_predict

def generate_daily_tips():
    matches = get_today_matches()
    if not matches:
        return "⚠️ No matches found for today from selected bookmakers."

    model = load_model_and_predict()
    selected_tips = []
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

            # ➕ Calculate Implied Probability
            implied_prob = 1 / odds
            model_prob = model.predict_proba([[home, away, team]])[0][1]  # This may vary by model structure
            ev = (odds * model_prob - 1) * 100

            # ✅ Apply EV and Odds Range Filter
            if ev >= 5 and 1.85 <= odds <= 3.50:
                selected_tips.append({
                    "match": f"{home} vs {away}",
                    "tip": team,
                    "odds": round(odds, 2),
                    "ev": round(ev, 2),
                    "bookie": bookie,
                    "time": match_time
                })

    if not selected_tips:
        return f"⚠️ No high-value tips found today within odds range 1.85–3.50."

    # Format final output
    message = f"🎯 AI-Generated Tips for {today_str}:\n"
    for tip in selected_tips:
        message += (
            f"\n🏟️ {tip['match']} @ {tip['time']}"
            f"\n📊 Tip: {tip['tip']} @ {tip['odds']} (Bookie: {tip['bookie']})"
            f"\n✅ EV: {tip['ev']}%\n"
        )

    return message

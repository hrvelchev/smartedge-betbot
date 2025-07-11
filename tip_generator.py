# tip_generator.py

from odds_fetcher import get_today_matches
import xgboost as xgb
import numpy as np
import pandas as pd

def load_model():
    model = xgb.Booster()
    model.load_model("model.xgb")
    return model

def preprocess_match(match):
    # Dummy encoding for now — replace with real features if available
    home = match["home_team"].lower()
    away = match["away_team"].lower()
    odds = match["odds"]

    home_odd = odds.get(match["home_team"], None)
    away_odd = odds.get(match["away_team"], None)
    draw_odd = odds.get("Draw", None)

    # Feature vector example (can be improved with team stats/ELO later)
    return {
        "home_odd": home_odd,
        "draw_odd": draw_odd,
        "away_odd": away_odd,
    }

def calculate_ev(prob, odd):
    return (prob * odd) - 1 if odd and prob else -999

def generate_daily_tips():
    model = load_model()
    matches = get_today_matches()
    selected_tips = []

    for match in matches:
        features = preprocess_match(match)
        if None in features.values():
            continue  # Skip if missing odds

        df = pd.DataFrame([features])
        dmatrix = xgb.DMatrix(df)
        preds = model.predict(dmatrix)

        outcomes = ["home_win", "draw", "away_win"]
        odds_keys = [match["home_team"], "Draw", match["away_team"]]

        for i, outcome in enumerate(outcomes):
            prob = preds[0][i] if len(preds.shape) > 1 else preds[i]
            odd = match["odds"].get(odds_keys[i], None)
            ev = calculate_ev(prob, odd)

            if ev > 0.05:
                tip = f"🏟️ {match['home_team']} vs {match['away_team']} @ {match['start_time']}\n" \
                      f"📊 Tip: {outcome.replace('_', ' ').title()} @ {odd:.2f} (Bookie: {match['bookmaker']})\n" \
                      f"✅ EV: {ev:.2%}\n"
                selected_tips.append(tip)

    if not selected_tips:
        return "📭 No high-EV bets found for today."

    today_str = pd.Timestamp.now().strftime('%Y-%m-%d')
    return f"🎯 AI-Generated Tips for {today_str}:\n\n" + "\n".join(selected_tips)

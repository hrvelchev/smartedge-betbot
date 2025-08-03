import xgboost as xgb
import pandas as pd
import numpy as np
import os

# Path to the pre‑trained XGBoost model.  When deploying the bot, ensure
# that ``model.xgb`` is present in the working directory or update this
# constant accordingly.
MODEL_PATH = "model.xgb"

def load_model_and_predict():
    """Load the XGBoost model and return a predictor object.

    The returned object exposes a ``predict_proba`` method that accepts a
    list of feature triplets [home_team, away_team, outcome] and returns a
    two‑column NumPy array with probabilities for [lose/draw, win].  Feature
    encoding is performed via simple hashing to integers, mirroring the
    training pipeline.
    """
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)

    def predict_proba(features_list):
        results = []
        for home, away, outcome in features_list:
            row = {
                "home_team": hash(home) % 10_000,
                "away_team": hash(away) % 10_000,
                "outcome": hash(outcome) % 10_000,
            }
            df = pd.DataFrame([row])
            prob = model.predict_proba(df)[0][1]
            results.append([1 - prob, prob])
        return np.array(results)

    class Predictor:
        def predict_proba(self, X):
            return predict_proba(X)

    return Predictor()
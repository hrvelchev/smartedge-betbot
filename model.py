import xgboost as xgb
import pandas as pd
import numpy as np
import os

MODEL_PATH = "model.xgb"

def load_model_and_predict():
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)

    def predict_proba(features_list):
        # features_list = list of [home_team, away_team, outcome]
        results = []
        for home, away, outcome in features_list:
            # Basic encoding logic – should match model training
            row = {
                "home_team": hash(home) % 10_000,
                "away_team": hash(away) % 10_000,
                "outcome": hash(outcome) % 10_000,
            }
            df = pd.DataFrame([row])
            prob = model.predict_proba(df)[0][1]
            results.append([1 - prob, prob])
        return np.array(results)

    # Return dummy object with predict_proba method
    class Predictor:
        def predict_proba(self, X):
            return predict_proba(X)

    return Predictor()
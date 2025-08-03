import xgboost as xgb
import pandas as pd
import numpy as np

# Path to the pre-trained XGBoost model.
MODEL_PATH = "model.xgb"

def load_model_and_predict():
    """
    Load the XGBoost model and return a predictor object.

    Uses Booster directly to avoid issues with n_classes_ attributes
    when loading a model trained elsewhere.
    """

    # Load the raw booster instead of XGBClassifier
    booster = xgb.Booster()
    booster.load_model(MODEL_PATH)

    def predict_proba(features_list):
        """
        Convert features (home, away, outcome) into hashed numeric features,
        build an xgboost DMatrix, and get probability predictions.
        """
        data = []
        for home, away, outcome in features_list:
            row = [
                hash(home) % 10_000,
                hash(away) % 10_000,
                hash(outcome) % 10_000,
            ]
            data.append(row)

        # Create a DMatrix for prediction
        dmatrix = xgb.DMatrix(np.array(data))

        # Booster.predict returns probabilities directly for binary classification
        probs = booster.predict(dmatrix)

        # Ensure correct shape: return [[1-p, p]] for each sample
        results = []
        for p in probs:
            p_val = float(p) if not isinstance(p, (list, np.ndarray)) else float(p[0])
            results.append([1 - p_val, p_val])

        return np.array(results)

    class Predictor:
        def predict_proba(self, X):
            return predict_proba(X)

    return Predictor()

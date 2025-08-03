import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# === Load and prepare your dataset ===
# Replace this with your actual dataset path
data = pd.read_csv("data/training_data.csv")

# Adjust these column names to match your dataset
X = data.drop(columns=["target"])
y = data["target"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# === Train the model ===
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    random_state=42,
    use_label_encoder=False,
    eval_metric="logloss"
)

print("Training model...")
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Validation accuracy: {acc:.4f}")

# === Save the trained model ===
joblib.dump(model, "model.pkl")
print("Model saved to model.pkl")

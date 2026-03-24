import pandas as pd
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# -----------------------------
# LOAD DATASET
# -----------------------------

df = pd.read_csv("vehicles.csv")

# -----------------------------
# BASIC CLEANING
# -----------------------------

df = df.dropna(subset=["year", "odometer", "price"])

# Remove unrealistic values
df = df[df["price"] > 1000]
df = df[df["price"] < 1000000]
df = df[df["odometer"] < 500000]
df = df[df["year"] > 1980]
df = df[df["year"] <= 2025]

# -----------------------------
# FEATURE ENGINEERING
# -----------------------------

current_year = 2025

df["car_age"] = current_year - df["year"]

# Log transform price (stabilizes prediction)
df["log_price"] = np.log1p(df["price"])

# -----------------------------
# FEATURES
# -----------------------------

features = [
    "year",
    "odometer",
    "car_age"
]

X = df[features]
y = df["log_price"]

# -----------------------------
# TRAIN TEST SPLIT
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# -----------------------------
# MODEL
# -----------------------------

model = RandomForestRegressor(
    n_estimators=500,
    max_depth=25,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# -----------------------------
# EVALUATION
# -----------------------------

preds_log = model.predict(X_test)

# convert predictions back to real price
preds_price = np.expm1(preds_log)
actual_price = np.expm1(y_test)

mae = mean_absolute_error(actual_price, preds_price)

print("Model 3 MAE (ZAR):", mae)

# -----------------------------
# FEATURE IMPORTANCE
# -----------------------------

importance = model.feature_importances_

for f, i in zip(features, importance):
    print(f"{f}: {i:.4f}")

# -----------------------------
# SAVE MODEL
# -----------------------------

joblib.dump(model, "deal_score_model.pkl")

print("Model 3 saved successfully")
print("Dataset size:", len(df))
print("Price range:", df["price"].min(), "-", df["price"].max())
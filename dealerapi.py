from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import joblib
import pandas as pd
from datetime import datetime
import os
import requests

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def root():
    return {"status": "API is running"}

EXCHANGE_RATE = 18

# -----------------------------
# MODEL DOWNLOAD LINKS (FIXED)
# -----------------------------
PRICE_MODEL_URL = "https://drive.google.com/uc?export=download&id=11b8EYK2lhqNI0KCvceh-_BpNtyQ3poTk"
SPEED_MODEL_URL = "https://drive.google.com/uc?export=download&id=19eOVHDOqWFCi-U_vfKvAEEplQmhgqFFq"
COLUMNS_URL = "https://drive.google.com/uc?export=download&id=1juBiA4Zaoh6FLrbMayZYVaxY63CjHLQ8"

# -----------------------------
# DOWNLOAD FUNCTION
# -----------------------------
def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"{filename} downloaded.")

# -----------------------------
# LOAD MODELS (SMART CACHE)
# -----------------------------
price_model = None
speed_model = None
model_columns = None

def load_models():
    global price_model, speed_model, model_columns

    if price_model is None:
        download_file(PRICE_MODEL_URL, "car_price_model.pkl")
        download_file(SPEED_MODEL_URL, "speed_model.pkl")
        download_file(COLUMNS_URL, "model_columns.pkl")

        price_model = joblib.load("car_price_model.pkl")
        speed_model = joblib.load("speed_model.pkl")
        model_columns = joblib.load("model_columns.pkl")

    return price_model, speed_model, model_columns

# -----------------------------
# DATA MODEL
# -----------------------------
class Vehicle(BaseModel):
    manufacturer: str
    condition: str
    fuel: str
    transmission: str
    drive: str
    type: str
    year: int
    odometer: int
    price: float

# -----------------------------
# FEATURE BUILDER
# -----------------------------
def build_price_features(df, model_columns):

    X = pd.DataFrame(0, index=df.index, columns=model_columns)

    for col in ["year", "odometer", "car_age"]:
        if col in df:
            X[col] = df[col]

    categorical = [
        "manufacturer",
        "condition",
        "fuel",
        "transmission",
        "drive",
        "type"
    ]

    for col in categorical:
        if col in df:
            for i, val in df[col].items():
                val = str(val).strip().lower()
                feature = f"{col}_{val}"
                if feature in X.columns:
                    X.at[i, feature] = 1

    return X

# -----------------------------
# VEHICLE ANALYZER API
# -----------------------------
@app.post("/analyze")
def analyze_vehicle(data: Vehicle):

    price_model, speed_model, model_columns = load_models()

    df = pd.DataFrame([data.dict()])
    df["car_age"] = datetime.now().year - df["year"]

    price_input = build_price_features(df, model_columns)

    predicted_price = price_model.predict(price_input)[0] * EXCHANGE_RATE
    sell_speed = speed_model.predict(df[["year","odometer","car_age"]])[0]

    profit = predicted_price - data.price

    if profit > 50000:
        deal_rating = "🔥 Great Deal"
    elif profit > 10000:
        deal_rating = "⚠️ Fair Deal"
    else:
        deal_rating = "❌ Bad Deal"

    return {
        "predicted_price": round(predicted_price,2),
        "profit": round(profit,2),
        "sell_speed": str(sell_speed),
        "deal_rating": deal_rating
    }

# -----------------------------
# INVENTORY ANALYZER API
# -----------------------------
@app.post("/inventory")
def analyze_inventory(data: List[Vehicle]):

    price_model, speed_model, model_columns = load_models()

    df = pd.DataFrame([d.dict() for d in data])
    df["car_age"] = datetime.now().year - df["year"]

    price_input = build_price_features(df, model_columns)

    df["predicted_price"] = price_model.predict(price_input) * EXCHANGE_RATE
    df["sell_speed"] = speed_model.predict(df[["year","odometer","car_age"]])
    df["potential_profit"] = df["predicted_price"] - df["price"]

    return df.to_dict(orient="records")

# -----------------------------
# MARKET SCANNER API
# -----------------------------
@app.post("/market")
def market_scan(data: List[Vehicle]):

    price_model, speed_model, model_columns = load_models()

    df = pd.DataFrame([d.dict() for d in data])
    df["car_age"] = datetime.now().year - df["year"]

    price_input = build_price_features(df, model_columns)

    df["predicted_price"] = price_model.predict(price_input) * EXCHANGE_RATE
    df["undervalue"] = df["predicted_price"] - df["price"]

    df = df.sort_values("undervalue", ascending=False)

    return df.to_dict(orient="records")
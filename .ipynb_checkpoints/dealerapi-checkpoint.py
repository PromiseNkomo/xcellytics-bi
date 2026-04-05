from fastapi import FastAPI, HTTPException
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

@app.get("/")
def root():
    return {"status": "API is running"}

EXCHANGE_RATE = 18

# -----------------------------
# GOOGLE DRIVE FILE IDS
# -----------------------------
PRICE_MODEL_ID = "11b8EYK2lhqNI0KCvceh-_BpNtyQ3poTk"
SPEED_MODEL_ID = "19eOVHDOqWFCi-U_vfKvAEEplQmhgqFFq"
COLUMNS_MODEL_ID = "1juBiA4Zaoh6FLrbMayZYVaxY63CjHLQ8"

# -----------------------------
# SAFE DOWNLOAD FUNCTION 🔥
# -----------------------------
def download_file(file_id, filename):

    if os.path.exists(filename):
        print(f"{filename} already exists")
        return

    print(f"⬇️ Downloading {filename}...")

    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()

    try:
        response = session.get(URL, params={"id": file_id}, stream=True, timeout=60)

        # ❗ Check if request failed
        if response.status_code != 200:
            raise Exception(f"Failed to download {filename} (status {response.status_code})")

        # Handle large file confirmation
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                response = session.get(
                    URL,
                    params={"id": file_id, "confirm": value},
                    stream=True,
                    timeout=60
                )

        with open(filename, "wb") as f:
            for chunk in response.iter_content(8192):
                if chunk:
                    f.write(chunk)

        # ✅ VALIDATION
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            raise Exception(f"{filename} download failed!")

        print(f"✅ {filename} downloaded successfully")

    except Exception as e:
        # ❗ Delete broken file if exists
        if os.path.exists(filename):
            os.remove(filename)
        raise Exception(str(e))

# -----------------------------
# LOAD MODELS (LAZY LOAD 🔥)
# -----------------------------
price_model = None
speed_model = None
model_columns = None

def load_models():
    global price_model, speed_model, model_columns

    if price_model is None:
        print("🚀 Loading models...")

        download_file(PRICE_MODEL_ID, "car_price_model.pkl")
        download_file(SPEED_MODEL_ID, "speed_model.pkl")
        download_file(COLUMNS_MODEL_ID, "model_columns.pkl")

        price_model = joblib.load("car_price_model.pkl")
        speed_model = joblib.load("speed_model.pkl")
        model_columns = joblib.load("model_columns.pkl")

        print("✅ Models loaded!")

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

    X["year"] = df["year"]
    X["odometer"] = df["odometer"]
    X["car_age"] = df["car_age"]

    for col in ["manufacturer","condition","fuel","transmission","drive","type"]:
        for i, val in df[col].items():
            feature = f"{col}_{str(val).lower()}"
            if feature in X.columns:
                X.loc[i, feature] = 1

    return X[model_columns]

# -----------------------------
# ANALYZE
# -----------------------------
@app.post("/analyze")
def analyze_vehicle(data: Vehicle):

    try:
        price_model, speed_model, model_columns = load_models()

        df = pd.DataFrame([data.dict()])
        df["car_age"] = datetime.now().year - df["year"]

        price_input = build_price_features(df, model_columns)

        predicted_price = price_model.predict(price_input)[0] * EXCHANGE_RATE

        speed_input = df[["year","odometer","car_age"]]
        sell_speed = speed_model.predict(speed_input)[0]

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

    except Exception as e:
        print("❌ ERROR:", str(e))
        return {"error": str(e)}

# -----------------------------
# INVENTORY
# -----------------------------
@app.post("/inventory")
def analyze_inventory(data: List[Vehicle]):

    try:
        price_model, speed_model, model_columns = load_models()

        df = pd.DataFrame([d.dict() for d in data])
        df["car_age"] = datetime.now().year - df["year"]

        price_input = build_price_features(df, model_columns)

        df["predicted_price"] = price_model.predict(price_input) * EXCHANGE_RATE
        df["sell_speed"] = speed_model.predict(df[["year","odometer","car_age"]])
        df["potential_profit"] = df["predicted_price"] - df["price"]

        return df.to_dict(orient="records")

    except Exception as e:
        print("❌ ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import joblib
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
import sqlite3
import hashlib
import uuid

app = FastAPI()

# CORS
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
FREE_LIMIT = 5  # 🔥 ADDED

# DATABASE
conn = sqlite3.connect("dealer.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    token TEXT,
    plan TEXT DEFAULT 'free',
    usage_count INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 0,
    expiry_date TEXT
)
""")
conn.commit()

# HELPERS
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_token():
    return str(uuid.uuid4())

# 🔥 UPDATED (expiry handling added)
def get_user(token: str):
    cursor.execute("SELECT * FROM users WHERE token=?", (token,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user[0]
    expiry = user[7]

    if expiry:
        expiry_date = datetime.fromisoformat(expiry)
        if datetime.now() > expiry_date:
            cursor.execute(
                "UPDATE users SET is_active=0, plan='free' WHERE id=?",
                (user_id,)
            )
            conn.commit()

            cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
            user = cursor.fetchone()

    return user

# MODELS
class UserAuth(BaseModel):
    email: str
    password: str

class Vehicle(BaseModel):
    manufacturer: Optional[str] = ""
    condition: Optional[str] = ""
    fuel: Optional[str] = ""
    transmission: Optional[str] = ""
    drive: Optional[str] = ""
    type: Optional[str] = ""
    year: int
    odometer: int
    price: float

# AUTH
@app.post("/signup")
def signup(user: UserAuth):
    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?,?)",
            (user.email, hash_password(user.password))
        )
        conn.commit()
        return {"message": "User created"}
    except:
        raise HTTPException(status_code=400, detail="User exists")

@app.post("/login")
def login(user: UserAuth):
    cursor.execute(
        "SELECT id FROM users WHERE email=? AND password=?",
        (user.email, hash_password(user.password))
    )
    u = cursor.fetchone()

    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token()
    cursor.execute("UPDATE users SET token=? WHERE id=?", (token, u[0]))
    conn.commit()

    return {"token": token}

@app.get("/me")
def get_me(token: str):
    user = get_user(token)
    return {
        "plan": user[4],
        "usage": user[5],
        "is_active": user[6],
        "expiry": user[7]
    }

# 🔥 IMPORTANT (this fixes your WhatsApp flow)
@app.get("/activate")
def activate_user(email: str):
    expiry = datetime.now() + timedelta(days=30)

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute(
        "UPDATE users SET plan='pro', is_active=1, expiry_date=? WHERE email=?",
        (expiry.isoformat(), email)
    )
    conn.commit()

    return {"message": f"{email} activated"}

# MODEL LOADING
PRICE_MODEL_ID = "11b8EYK2lhqNI0KCvceh-_BpNtyQ3poTk"
SPEED_MODEL_ID = "19eOVHDOqWFCi-U_vfKvAEEplQmhgqFFq"
COLUMNS_MODEL_ID = "1juBiA4Zaoh6FLrbMayZYVaxY63CjHLQ8"

def download_file(file_id, filename):
    if os.path.exists(filename):
        return
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)

    with open(filename, "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)

price_model = None
speed_model = None
model_columns = None

def load_models():
    global price_model, speed_model, model_columns
    if price_model is None:
        download_file(PRICE_MODEL_ID, "car_price_model.pkl")
        download_file(SPEED_MODEL_ID, "speed_model.pkl")
        download_file(COLUMNS_MODEL_ID, "model_columns.pkl")

        price_model = joblib.load("car_price_model.pkl")
        speed_model = joblib.load("speed_model.pkl")
        model_columns = joblib.load("model_columns.pkl")

    return price_model, speed_model, model_columns

def build_price_features(df, model_columns):
    X = pd.DataFrame(0, index=df.index, columns=model_columns)

    X["year"] = df["year"]
    X["odometer"] = df["odometer"]
    X["car_age"] = df["car_age"]

    for col in ["manufacturer","condition","fuel","transmission","drive","type"]:
        for i, val in df[col].fillna("").items():
            feature = f"{col}_{str(val).lower()}"
            if feature in X.columns:
                X.loc[i, feature] = 1

    return X[model_columns]

# ANALYZE
@app.post("/analyze")
def analyze_vehicle(data: Vehicle, token: str):

    user = get_user(token)

    # 🔥 PAYMENT CONTROL ADDED
    if user[6] == 0:  # not active
        if user[5] >= FREE_LIMIT:
            raise HTTPException(status_code=403, detail="Free limit reached. Upgrade required.")

    price_model, speed_model, model_columns = load_models()

    df = pd.DataFrame([data.dict()])
    df["car_age"] = datetime.now().year - df["year"]

    price_input = build_price_features(df, model_columns)

    predicted_price = float(price_model.predict(price_input)[0] * EXCHANGE_RATE)
    profit = float(predicted_price - data.price)

    # 🔥 USAGE TRACKING ADDED
    cursor.execute(
        "UPDATE users SET usage_count = usage_count + 1 WHERE id=?",
        (user[0],)
    )
    conn.commit()

    return {
        "profit": round(profit, 2)
    }

# INVENTORY
@app.post("/inventory")
def analyze_inventory(data: List[Vehicle], token: str):

    user = get_user(token)

    # 🔥 PAYMENT LOCK ADDED
    if user[6] == 0:
        raise HTTPException(status_code=403, detail="Upgrade required for bulk analysis")

    price_model, speed_model, model_columns = load_models()

    results = []

    for vehicle in data:
        df = pd.DataFrame([vehicle.dict()])
        df["car_age"] = datetime.now().year - df["year"]

        price_input = build_price_features(df, model_columns)

        predicted_price = float(price_model.predict(price_input)[0] * EXCHANGE_RATE)
        profit = float(predicted_price - vehicle.price)

        results.append({
            "manufacturer": str(vehicle.manufacturer),
            "year": int(vehicle.year),
            "price": float(vehicle.price),
            "predicted_price": round(predicted_price, 2),
            "profit": round(profit, 2)
        })

    return results
import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import bcrypt

# -----------------------------
# CONFIG
# -----------------------------

EXCHANGE_RATE = 18  # USD → ZAR

st.set_page_config(
    page_title="AI Dealer Intelligence SA",
    page_icon="🚗",
    layout="wide"
)

# -----------------------------
# DOWNLOAD FUNCTION
# -----------------------------

def download_csv(df, filename="results.csv"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Results",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

# -----------------------------
# LOGIN SYSTEM
# -----------------------------

users = {
    "dealer1@gmail.com": bcrypt.hashpw("1234".encode(), bcrypt.gensalt()),
    "dealer2@gmail.com": bcrypt.hashpw("1234".encode(), bcrypt.gensalt())
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "dealer_inventory" not in st.session_state:
    st.session_state.dealer_inventory = None

if "market_data" not in st.session_state:
    st.session_state.market_data = None


def login():
    st.title("🚗 AI Dealer Intelligence SA")

    email = st.text_input("Dealer Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in users:
            if bcrypt.checkpw(password.encode(), users[email]):
                st.session_state.logged_in = True
                st.session_state.dealer = email
                st.rerun()
            else:
                st.error("Invalid password")
        else:
            st.error("User not found")


if not st.session_state.logged_in:
    login()
    st.stop()

# -----------------------------
# LOAD MODELS
# -----------------------------

price_model = joblib.load("car_price_model.pkl")
speed_model = joblib.load("speed_model.pkl")
model_columns = joblib.load("model_columns.pkl")

# -----------------------------
# FEATURE BUILDER
# -----------------------------

def build_price_features(df):

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
# SIDEBAR
# -----------------------------

st.sidebar.title("🚗 Dealer AI System")
st.sidebar.write(f"Logged in: {st.session_state.dealer}")

page = st.sidebar.radio(
    "Navigation",
    [
        "About",
        "Disclaimer",
        "Home",
        "Vehicle Analyzer",
        "Dealer Inventory Upload",
        "Market Scanner",
        "Inventory Insights"
    ]
)

# -----------------------------
# ABOUT
# -----------------------------

if page == "About":

    st.title("About AI Dealer Intelligence SA")

    st.markdown("""
### 🚗 Overview
AI Dealer Intelligence SA is a **machine learning-powered decision support system**
built specifically for the South African automotive market.

It helps dealerships:
- Identify **profitable vehicles**
- Detect **undervalued market opportunities**
- Predict **resale value and selling speed**
- Make **data-driven inventory decisions**

---

### ⚙️ How It Works
The system uses trained machine learning models to:
- Estimate vehicle market value
- Predict selling speed
- Analyze profitability potential

---

### 🎯 Purpose
This platform is a **decision-support tool**, not a replacement for dealer expertise.

---

### 🇿🇦 Built for South Africa
All outputs are converted into **ZAR**.
""")

# -----------------------------
# DISCLAIMER
# -----------------------------

elif page == "Disclaimer":

    st.title("Disclaimer")

    st.markdown("""
### ⚠️ Important Notice

This system provides **AI-generated predictions**.

- Not financial advice  
- No guarantee of profit  
- Market conditions may vary  

---

### Limitations
Does not account for:
- Accident history  
- Hidden damage  
- Negotiation factors  

---

### Liability
Use at your own risk.  
Developers are not liable for losses.

---

Use AI as a guide — not a final decision-maker.
""")

# -----------------------------
# HOME
# -----------------------------

elif page == "Home":

    st.title("🚗 AI Dealer Intelligence SA")
    st.markdown("### Smart Decisions. Better Deals. Higher Profits.")

    st.info("Welcome to your AI-powered dealership dashboard.")

    if st.session_state.dealer_inventory is not None:
        df = st.session_state.dealer_inventory

        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Vehicles", len(df))
        col2.metric("Avg Profit", f"R {round(df['potential_profit'].mean(),2)}")
        col3.metric("Best Deal", f"R {round(df['potential_profit'].max(),2)}")
        col4.metric("Fast Sellers", (df["sell_speed"]=="FAST").sum())

        fig, ax = plt.subplots()
        ax.hist(df["potential_profit"], bins=20)
        st.pyplot(fig)

    else:
        st.warning("Upload inventory to see insights.")

# -----------------------------
# VEHICLE ANALYZER
# -----------------------------

elif page == "Vehicle Analyzer":

    st.title("Vehicle Deal Analyzer")

    manufacturer = st.selectbox("Manufacturer", ["toyota","ford","volkswagen","bmw","audi"])
    condition = st.selectbox("Condition",["excellent","good","fair"])
    fuel = st.selectbox("Fuel",["gas","diesel","hybrid","electric"])
    transmission = st.selectbox("Transmission",["automatic","manual"])
    drive = st.selectbox("Drive",["fwd","rwd","4wd"])
    type_ = st.selectbox("Vehicle Type",["sedan","suv","pickup","hatchback"])

    year = st.number_input("Year",1995,2025,2020)
    odometer = st.number_input("Mileage",0,300000,40000)
    price = st.number_input("Dealer Price (ZAR)",0,2000000,200000)

    if st.button("Analyze Deal"):

        car_age = datetime.now().year - year

        df = pd.DataFrame({
            "year":[year],
            "odometer":[odometer],
            "car_age":[car_age],
            "manufacturer":[manufacturer],
            "condition":[condition],
            "fuel":[fuel],
            "transmission":[transmission],
            "drive":[drive],
            "type":[type_]
        })

        price_input = build_price_features(df)

        predicted_price = price_model.predict(price_input)[0] * EXCHANGE_RATE
        sell_speed = speed_model.predict(df[["year","odometer","car_age"]])[0]
        profit = predicted_price - price

        if profit > 50000:
            deal_rating = "🔥 Great Deal"
        elif profit > 10000:
            deal_rating = "⚠️ Fair Deal"
        else:
            deal_rating = "❌ Bad Deal"

        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Estimated Value",f"R {round(predicted_price,2)}")
        col2.metric("Potential Profit",f"R {round(profit,2)}")
        col3.metric("Sell Speed",sell_speed)
        col4.metric("Deal Rating", deal_rating)

        result_df = pd.DataFrame({
            "manufacturer":[manufacturer],
            "condition":[condition],
            "fuel":[fuel],
            "transmission":[transmission],
            "drive":[drive],
            "type":[type_],
            "year":[year],
            "odometer":[odometer],
            "dealer_price":[price],
            "predicted_price":[predicted_price],
            "sell_speed":[sell_speed],
            "potential_profit":[profit],
            "deal_rating":[deal_rating]
        })

        download_csv(result_df, "vehicle_analysis.csv")

# -----------------------------
# DEALER INVENTORY UPLOAD
# -----------------------------

elif page == "Dealer Inventory Upload":

    st.title("Dealer Inventory AI Analyzer")

    file = st.file_uploader("Upload Dealer CSV")

    if file:
        dealer_df = pd.read_csv(file)
        dealer_df.columns = dealer_df.columns.str.lower()

        for col in ["manufacturer","condition","fuel","transmission","drive","type"]:
            if col in dealer_df:
                dealer_df[col] = dealer_df[col].astype(str).str.lower()

        dealer_df["car_age"] = datetime.now().year - dealer_df["year"]

        price_input = build_price_features(dealer_df)

        dealer_df["predicted_price"] = price_model.predict(price_input) * EXCHANGE_RATE

        dealer_df["sell_speed"] = speed_model.predict(
            dealer_df[["year","odometer","car_age"]]
        )

        dealer_df["potential_profit"] = dealer_df["predicted_price"] - dealer_df["price"]

        st.session_state.dealer_inventory = dealer_df

    if st.session_state.dealer_inventory is not None:

        df = st.session_state.dealer_inventory

        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Vehicles",len(df))
        col2.metric("Avg Profit",f"R {round(df['potential_profit'].mean(),2)}")
        col3.metric("Best Deal",f"R {round(df['potential_profit'].max(),2)}")
        col4.metric("Fast Sellers",(df["sell_speed"]=="FAST").sum())

        fig, ax = plt.subplots()
        ax.hist(df["potential_profit"], bins=20)
        st.pyplot(fig)

        st.dataframe(df)

        download_csv(df, "dealer_inventory_results.csv")

# -----------------------------
# MARKET SCANNER
# -----------------------------

elif page == "Market Scanner":

    st.title("Market Scanner")

    file = st.file_uploader("Upload Market CSV")

    if file:

        df = pd.read_csv(file)
        df.columns = df.columns.str.lower()

        df["car_age"] = datetime.now().year - df["year"]

        price_input = build_price_features(df)

        df["predicted_price"] = price_model.predict(price_input) * EXCHANGE_RATE

        df["undervalue"] = df["predicted_price"] - df["price"]

        result_df = df.sort_values("undervalue",ascending=False)

        st.dataframe(result_df.head(20))

        download_csv(result_df, "market_opportunities.csv")

# -----------------------------
# INVENTORY INSIGHTS
# -----------------------------

elif page == "Inventory Insights":

    st.title("Inventory Insights")

    if st.session_state.dealer_inventory is not None:

        df = st.session_state.dealer_inventory

        fig, ax = plt.subplots()
        ax.hist(df["potential_profit"], bins=20)
        st.pyplot(fig)
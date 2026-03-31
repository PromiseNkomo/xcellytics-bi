from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import joblib
import pandas as pd
import shap
import sqlite3
from datetime import datetime
import io

app = FastAPI(title="ZimCred AI Engine")

# -----------------------------
# Load Trained Engine
# -----------------------------
engine = joblib.load("zimcred_engine.pkl")
model = engine["model"]
feature_columns = engine["feature_columns"]
medians = engine["medians"]

explainer = shap.TreeExplainer(model)

# -----------------------------
# Database Setup
# -----------------------------
conn = sqlite3.connect("zimcred.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS credit_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    monthly_income REAL,
    requested_loan REAL,
    monthly_expenses REAL,
    dependents INTEGER,
    probability_default REAL,
    credit_score INTEGER,
    risk_band TEXT,
    recommended_limit REAL
)
""")
conn.commit()

# -----------------------------
# Request Schema
# -----------------------------
class ApplicantRequest(BaseModel):
    monthly_income: float
    requested_loan_amount: float
    monthly_expenses: float
    dependents: int

# -----------------------------
# Build Model Row
# -----------------------------
def build_applicant_row(real_input):
    row = {col: medians.get(col, 0) for col in feature_columns}
    row.update(real_input)
    return pd.DataFrame([row])

# -----------------------------
# Scoring Logic
# -----------------------------
def zimcred_score(applicant_df):

    prob = model.predict_proba(applicant_df)[:, 1][0]
    credit_score = int(850 - (prob * 550))

    if prob < 0.2:
        band = "Low Risk"
    elif prob < 0.4:
        band = "Medium Risk"
    elif prob < 0.6:
        band = "High Risk"
    else:
        band = "Very High Risk"

    recommended_limit = (
        0
        if band in ["High Risk", "Very High Risk"]
        else float(applicant_df["AMT_CREDIT"].values[0] * 0.9)
    )

    return prob, credit_score, band, recommended_limit

# -----------------------------
# SINGLE SCORING
# -----------------------------
@app.post("/score")
def score_applicant(applicant: ApplicantRequest):

    credit_profile = {
        "AMT_INCOME_TOTAL": applicant.monthly_income * 12,
        "AMT_CREDIT": applicant.requested_loan_amount,
        "AMT_ANNUITY": applicant.monthly_expenses,
        "CNT_CHILDREN": applicant.dependents
    }

    applicant_df = build_applicant_row(credit_profile)

    prob, credit_score, band, recommended_limit = zimcred_score(applicant_df)

    # Save to DB
    cursor.execute("""
    INSERT INTO credit_decisions (
        timestamp,
        monthly_income,
        requested_loan,
        monthly_expenses,
        dependents,
        probability_default,
        credit_score,
        risk_band,
        recommended_limit
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        applicant.monthly_income,
        applicant.requested_loan_amount,
        applicant.monthly_expenses,
        applicant.dependents,
        round(float(prob), 4),
        credit_score,
        band,
        recommended_limit
    ))
    conn.commit()

    return {
        "Probability_of_Default": round(float(prob), 4),
        "Credit_Score": credit_score,
        "Risk_Band": band,
        "Recommended_Loan_Limit": recommended_limit
    }

# -----------------------------
# 🚀 BULK SCORING (NEW)
# -----------------------------
@app.post("/bulk-score")
async def bulk_score(file: UploadFile = File(...)):

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    results = []

    for _, row in df.iterrows():

        applicant = {
            "AMT_INCOME_TOTAL": row["monthly_income"] * 12,
            "AMT_CREDIT": row["requested_loan_amount"],
            "AMT_ANNUITY": row["monthly_expenses"],
            "CNT_CHILDREN": row["dependents"]
        }

        applicant_df = build_applicant_row(applicant)

        prob, score, band, limit = zimcred_score(applicant_df)

        results.append({
            "monthly_income": row["monthly_income"],
            "requested_loan_amount": row["requested_loan_amount"],
            "monthly_expenses": row["monthly_expenses"],
            "dependents": row["dependents"],
            "Probability_of_Default": round(float(prob), 4),
            "Credit_Score": score,
            "Risk_Band": band,
            "Recommended_Loan_Limit": limit
        })

    return {
        "results": results,
        "total_processed": len(results)
    }

# -----------------------------
# HISTORY
# -----------------------------
@app.get("/history")
def get_history():
    cursor.execute("SELECT * FROM credit_decisions ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()

    columns = [
        "id", "timestamp", "monthly_income", "requested_loan",
        "monthly_expenses", "dependents",
        "probability_default", "credit_score",
        "risk_band", "recommended_limit"
    ]

    results = [dict(zip(columns, row)) for row in rows]

    return {"Recent_Decisions": results}

# -----------------------------
# HEALTH
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ZimCred AI Bureau Engine Running"}
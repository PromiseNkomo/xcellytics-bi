from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
import requests

app = FastAPI()

SCORING_API = "http://127.0.0.1:8000/score"
AGENT_API = "http://127.0.0.1:8001/assist"

API_KEY = "zimcapital-secret-key"
MFI_NAME = "ZimCapital Microfinance"


def parse_message(body: str):

    body = body.replace(",", " ")
    parts = body.split()

    data = {}

    for i in range(len(parts)):
        if parts[i].lower() == "income:":
            data["income"] = parts[i + 1]
        elif parts[i].lower() == "loan:":
            data["loan"] = parts[i + 1]
        elif parts[i].lower() == "expenses:":
            data["expenses"] = parts[i + 1]
        elif parts[i].lower() == "dependents:":
            data["dependents"] = parts[i + 1]

    return {
        "monthly_income": float(data.get("income", 0)),
        "requested_loan_amount": float(data.get("loan", 0)),
        "monthly_expenses": float(data.get("expenses", 0)),
        "dependents": int(data.get("dependents", 0))
    }


@app.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...)):

    applicant_data = parse_message(Body)

    # ------------------------
    # STEP 1: Credit Scoring
    # ------------------------

    scoring_response = requests.post(
        SCORING_API,
        json=applicant_data
    )

    if scoring_response.status_code != 200:
        return PlainTextResponse("ZimCred AI error: scoring engine unavailable.")

    scoring_result = scoring_response.json()

    # ------------------------
    # STEP 2: AI Explanation
    # ------------------------

    agent_payload = {
        "question": "Explain this loan decision",
        "mfi_name": MFI_NAME,
        "applicant_data": applicant_data
    }

    agent_response = requests.post(
        AGENT_API,
        json=agent_payload,
        headers={
            "X-API-Key": API_KEY
        }
    )

    explanation = "Explanation unavailable"

    if agent_response.status_code == 200:
        agent_data = agent_response.json()

        assistant = agent_data.get("assistant", {})

        explanation = assistant.get("summary", "Explanation unavailable")

    # ------------------------
    # STEP 3: Format WhatsApp Response
    # ------------------------

    credit_score = scoring_result.get("Credit_Score")
    risk_band = scoring_result.get("Risk_Band")
    loan_limit = scoring_result.get("Recommended_Loan_Limit")
    probability = scoring_result.get("Probability_of_Default")

    message = f"""
ZimCred AI Decision

Credit Score: {credit_score}
Risk Band: {risk_band}
Loan Limit: {loan_limit}
Probability of Default: {probability}

Explanation:
{explanation}
"""

    return PlainTextResponse(message)


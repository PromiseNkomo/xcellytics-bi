from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
import requests

app = FastAPI()

SCORING_API = "http://127.0.0.1:8000/score"
AGENT_API = "http://127.0.0.1:8001/assist"

def parse_message(body: str):
    """
    Expected format:

    Income: 1200
    Loan: 500
    Expenses: 400
    Dependents: 2
    """

    lines = body.split("\n")
    data = {}

    for line in lines:
        if ":" in line:
            key, value = line.split(":")
            data[key.strip().lower()] = value.strip()

    return {
        "monthly_income": float(data.get("income", 0)),
        "requested_loan_amount": float(data.get("loan", 0)),
        "monthly_expenses": float(data.get("expenses", 0)),
        "dependents": int(data.get("dependents", 0))
    }


@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...)
):

    applicant_data = parse_message(Body)

    # Step 1: Call Scoring API
    scoring_response = requests.post(
        SCORING_API,
        json=applicant_data
    )

    if scoring_response.status_code != 200:
        return PlainTextResponse("System error. Try again later.")

    scoring_result = scoring_response.json()

    # Step 2: Call AI Agent
    agent_payload = {
        "question": "Explain this loan decision",
        "mfi_name": "ZimCred WhatsApp",
        "applicant_data": applicant_data
    }

    agent_response = requests.post(
        AGENT_API,
        json=agent_payload
    )

    explanation = "Explanation unavailable"

    if agent_response.status_code == 200:
        explanation = agent_response.json().get("assistant", "")

    # Step 3: Format WhatsApp Response
    message = f"""
ZimCred AI Decision

Credit Score: {scoring_result.get("credit_score")}
Risk Band: {scoring_result.get("risk_band")}
Loan Limit: {scoring_result.get("recommended_loan_limit")}
Status: {scoring_result.get("policy_status")}

Explanation:
{explanation}
"""

    return PlainTextResponse(message)
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import requests

app = FastAPI(title="ZimCred AI Loan Officer Assistant")

# =====================================================
# Configuration
# =====================================================

ZIMCRED_API_URL = "http://127.0.0.1:8000"

# =====================================================
# Internal MFI Policy Store
# =====================================================

MFI_POLICIES = {
    "ZimCapital Microfinance": {
        "approval_threshold": 0.50
    },
    "TrustFund MFI": {
        "approval_threshold": 0.45
    },
    "Unity Finance": {
        "approval_threshold": 0.55
    }
}

# =====================================================
# API Key Security Layer
# =====================================================

API_KEYS = {
    "zimcapital-secret-key": "ZimCapital Microfinance",
    "trustfund-secret-key": "TrustFund MFI",
    "unity-secret-key": "Unity Finance"
}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")

    if api_key in API_KEYS:
        return API_KEYS[api_key]

    raise HTTPException(status_code=403, detail="Invalid API Key")


# =====================================================
# Request Schemas
# =====================================================

class AgentRequest(BaseModel):
    question: str
    applicant_data: dict
    mfi_name: str
    simulate: bool = False


class ChatRequest(BaseModel):
    message: str
    mfi_name: str


# =====================================================
# Scoring Engine Connector
# =====================================================

def get_zimcred_decision(applicant_data):

    try:
        response = requests.post(
            f"{ZIMCRED_API_URL}/score",
            json=applicant_data,
            timeout=5
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Scoring engine returned an error"
            )

        return response.json()

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to scoring engine"
        )


# =====================================================
# Simulation Engine
# =====================================================

def simulate_applicant(applicant_data):

    try:
        response = requests.post(
            f"{ZIMCRED_API_URL}/score",
            json=applicant_data,
            timeout=5
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Simulation failed - scoring engine error"
            )

        return response.json()

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Simulation failed - unable to reach scoring engine"
        )


# =====================================================
# Fetch MFI Policy
# =====================================================

def get_mfi_policy(mfi_name):

    policy = MFI_POLICIES.get(mfi_name)

    if not policy:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown MFI: {mfi_name}"
        )

    return policy


# =====================================================
# Decision Panel Builder
# =====================================================

def build_decision_panel(decision, approval_threshold):

    pd = float(decision.get("Probability_of_Default", 0.0))
    score = int(decision.get("Credit_Score", 0))
    risk = decision.get("Risk_Band", "Unknown")
    limit = int(decision.get("Recommended_Loan_Limit", 0))

    if pd > approval_threshold:
        policy_status = "Declined"
    else:
        policy_status = "Approved"

    if pd < 0.30:
        confidence = "High Confidence"
    elif pd <= 0.50:
        confidence = "Moderate Confidence"
    else:
        confidence = "Low Confidence"

    return {
        "Probability_of_Default": round(pd, 4),
        "Credit_Score": score,
        "Risk_Band": risk,
        "Recommended_Loan_Limit": limit,
        "Policy_Status": policy_status,
        "Confidence_Level": confidence
    }


# =====================================================
# Assistant Narrative Engine
# =====================================================

def build_assistant_response(decision_panel, mfi_name, approval_threshold):

    pd = decision_panel["Probability_of_Default"]
    score = decision_panel["Credit_Score"]
    risk = decision_panel["Risk_Band"]
    limit = decision_panel["Recommended_Loan_Limit"]
    status = decision_panel["Policy_Status"]

    if risk == "Low Risk":
        risk_note = "The applicant demonstrates strong repayment capacity."
    elif risk == "Medium Risk":
        risk_note = "The applicant presents moderate credit exposure requiring monitoring."
    elif risk == "High Risk":
        risk_note = "The applicant reflects elevated repayment uncertainty."
    else:
        risk_note = "The applicant falls into a critical risk classification."

    if status == "Declined":
        policy_note = (
            f"This exceeds {mfi_name}'s approved probability of default threshold "
            f"of {approval_threshold:.2f}."
        )
        recommended_action = "Loan application should be declined or restructured."
    else:
        policy_note = (
            f"This falls within {mfi_name}'s approved probability of default threshold "
            f"of {approval_threshold:.2f}."
        )
        recommended_action = "Loan may proceed within recommended exposure limits."

    summary = (
        f"The applicant has a probability of default of {pd:.2f} "
        f"with a credit score of {score}, classified as {risk}. "
        f"{risk_note}"
    )

    return {
        "summary": summary,
        "risk_analysis": risk_note,
        "policy_reference": policy_note,
        "recommended_action": recommended_action
    }


# =====================================================
# Loan Decision Endpoint
# =====================================================

@app.post("/assist")
def assist(
    request: AgentRequest,
    mfi_from_key: str = Depends(verify_api_key)
):

    if request.mfi_name != mfi_from_key:
        raise HTTPException(
            status_code=403,
            detail="MFI name does not match API key authorization"
        )

    raw_decision = get_zimcred_decision(request.applicant_data)

    decision = raw_decision.get("decision", raw_decision)

    policy = get_mfi_policy(request.mfi_name)
    approval_threshold = policy["approval_threshold"]

    decision_panel = build_decision_panel(decision, approval_threshold)

    assistant = build_assistant_response(
        decision_panel,
        request.mfi_name,
        approval_threshold
    )

    return {
        "mfi": request.mfi_name,
        "decision_panel": decision_panel,
        "assistant": assistant
    }


# =====================================================
# Chat Agent Endpoint
# =====================================================

@app.post("/chat")
def chat_agent(
    request: ChatRequest,
    mfi_from_key: str = Depends(verify_api_key)
):

    if request.mfi_name != mfi_from_key:
        raise HTTPException(
            status_code=403,
            detail="MFI name does not match API key authorization"
        )

    message = request.message.lower()

    if "history" in message:

        try:
            response = requests.get(f"{ZIMCRED_API_URL}/history")
            history_data = response.json()

            return {
                "agent_reply": "Here are the most recent credit decisions.",
                "data": history_data
            }

        except:
            raise HTTPException(status_code=500, detail="Unable to fetch history")

    elif "health" in message or "status" in message:

        return {
            "agent_reply": "ZimCred AI system is running normally."
        }

    elif "simulate" in message:

        return {
            "agent_reply": "To run a simulation use the /assist endpoint and set simulate=true with new applicant data."
        }

    else:

        return {
            "agent_reply": "I can help with credit decisions, risk explanations, simulations, or retrieving credit decision history."
        }


# =====================================================
# Health Check
# =====================================================

@app.get("/health")
def health():
    return {"status": "ZimCred AI Loan Officer Assistant Running (Hybrid Mode)"}
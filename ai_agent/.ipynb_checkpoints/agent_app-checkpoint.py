from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re

# 🔐 NEW IMPORTS (LOGIN)
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI(title="ZimCred AI Loan Officer Assistant")

# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 🔐 AUTH CONFIG (NEW)
# =====================================================

SECRET_KEY = "supersecretkey"  # 🔥 change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fake DB (we upgrade later)
fake_users_db = {}

# =====================================================
# CONFIG
# =====================================================

ZIMCRED_API_URL = "http://127.0.0.1:8000"

# =====================================================
# MFI POLICY
# =====================================================

MFI_POLICIES = {
    "ZimCapital Microfinance": {
        "approval_threshold": 0.50
    }
}

# =====================================================
# API KEY SECURITY (UNCHANGED)
# =====================================================

API_KEYS = {
    "zimcapital-secret-key": "ZimCapital Microfinance"
}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key required")

    if api_key in API_KEYS:
        return API_KEYS[api_key]

    raise HTTPException(status_code=403, detail="Invalid API Key")

# =====================================================
# 🔐 AUTH FUNCTIONS (NEW)
# =====================================================

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# =====================================================
# 🔐 AUTH SCHEMAS (NEW)
# =====================================================

class User(BaseModel):
    username: str
    password: str

# =====================================================
# 🔐 AUTH ENDPOINTS (NEW)
# =====================================================

@app.post("/register")
def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    fake_users_db[user.username] = {
        "username": user.username,
        "hashed_password": hash_password(user.password)
    }

    return {"message": "User registered successfully"}


@app.post("/login")
def login(user: User):
    db_user = fake_users_db.get(user.username)

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}

# =====================================================
# SCHEMAS (UNCHANGED)
# =====================================================

class AgentRequest(BaseModel):
    question: str
    applicant_data: dict
    mfi_name: str


class ChatRequest(BaseModel):
    message: str
    mfi_name: str

# =====================================================
# CONNECT TO SCORING ENGINE
# =====================================================

def get_zimcred_decision(applicant_data):

    try:
        response = requests.post(
            f"{ZIMCRED_API_URL}/score",
            json=applicant_data,
            timeout=5
        )

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Scoring engine error")

        return response.json()

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Cannot connect to scoring engine")

# =====================================================
# BUILD DECISION PANEL
# =====================================================

def build_decision_panel(decision, threshold):

    pd = float(decision.get("Probability_of_Default", 0))
    score = int(decision.get("Credit_Score", 0))
    risk = decision.get("Risk_Band", "Unknown")
    limit = float(decision.get("Recommended_Loan_Limit", 0))

    status = "Declined" if pd > threshold else "Approved"

    return {
        "Probability_of_Default": round(pd, 4),
        "Credit_Score": score,
        "Risk_Band": risk,
        "Recommended_Loan_Limit": limit,
        "Policy_Status": status
    }

# =====================================================
# AI EXPLANATION ENGINE
# =====================================================

def build_assistant_response(panel, mfi_name, threshold):

    pd = panel["Probability_of_Default"]
    score = panel["Credit_Score"]
    risk = panel["Risk_Band"]
    status = panel["Policy_Status"]

    if risk == "Low Risk":
        risk_note = "The applicant demonstrates strong repayment capacity and low credit exposure."
    elif risk == "Medium Risk":
        risk_note = "The applicant presents moderate credit exposure and should be monitored."
    elif risk == "High Risk":
        risk_note = "The applicant shows elevated repayment risk requiring caution."
    else:
        risk_note = "The applicant falls into a critical risk category with high likelihood of default."

    policy_note = (
        f"This falls within {mfi_name}'s approval threshold ({threshold:.2f})."
        if status == "Approved"
        else f"This exceeds {mfi_name}'s approval threshold ({threshold:.2f})."
    )

    recommendation = (
        "Loan can be approved within recommended limits."
        if status == "Approved"
        else "Loan should be declined or restructured."
    )

    return {
        "summary": f"Applicant scored {score} with a {risk} classification and probability of default of {pd:.2f}.",
        "risk_analysis": risk_note,
        "policy_reference": policy_note,
        "recommended_action": recommendation
    }

# =====================================================
# MAIN ENDPOINT (UNCHANGED)
# =====================================================

@app.post("/assist")
def assist(
    request: AgentRequest,
    mfi_from_key: str = Depends(verify_api_key)
):

    if request.mfi_name != mfi_from_key:
        raise HTTPException(status_code=403, detail="Unauthorized MFI")

    raw = get_zimcred_decision(request.applicant_data)

    threshold = MFI_POLICIES[request.mfi_name]["approval_threshold"]

    decision_panel = build_decision_panel(raw, threshold)

    assistant = build_assistant_response(
        decision_panel,
        request.mfi_name,
        threshold
    )

    return {
        "decision_panel": decision_panel,
        "assistant": assistant
    }

# =====================================================
# 🧠 CHATBOT (UNCHANGED - YOUR GOOD VERSION)
# =====================================================

def extract_numbers(text):
    numbers = re.findall(r"\d+", text)
    return list(map(int, numbers))


@app.post("/chat")
def chat_agent(request: ChatRequest):

    msg = request.message.lower()
    numbers = extract_numbers(msg)

    if len(numbers) >= 4:
        try:
            income, loan, expenses, dependents = numbers[:4]

            applicant_data = {
                "monthly_income": income,
                "requested_loan_amount": loan,
                "monthly_expenses": expenses,
                "dependents": dependents
            }

            raw = get_zimcred_decision(applicant_data)
            threshold = MFI_POLICIES[request.mfi_name]["approval_threshold"]
            panel = build_decision_panel(raw, threshold)

            explanation = build_assistant_response(
                panel,
                request.mfi_name,
                threshold
            )

            return {
                "agent_reply": f"""
📊 Loan Assessment Result:

• Credit Score: {panel['Credit_Score']}
• Risk Level: {panel['Risk_Band']}
• Probability of Default: {panel['Probability_of_Default']}
• Decision: {panel['Policy_Status']}

🧠 Analysis:
{explanation['risk_analysis']}

📌 Recommendation:
{explanation['recommended_action']}
"""
            }

        except:
            return {"agent_reply": "I detected financial inputs but failed to process them."}

    if any(word in msg for word in ["hello", "hi", "hey"]):
        return {"agent_reply": "Hello 👋 I am ZimCred AI. Ask me to evaluate a loan."}

    elif "help" in msg:
        return {"agent_reply": "Provide income, loan, expenses, dependents and I will evaluate."}

    return {"agent_reply": "Provide applicant numbers and I will assess the loan."}

# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():
    return {"status": "ZimCred AI Assistant Running"}
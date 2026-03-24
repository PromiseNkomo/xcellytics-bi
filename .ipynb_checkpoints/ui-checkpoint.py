import streamlit as st
import requests
import pandas as pd

ASSIST_API = "http://127.0.0.1:8001/assist"
CHAT_API = "http://127.0.0.1:8001/chat"
HEALTH_API = "http://127.0.0.1:8001/health"

st.set_page_config(page_title="ZimCred AI", layout="wide")

# =====================================================
# HEADER
# =====================================================

st.title("ZimCred AI")
st.subheader("Intelligent Credit Risk Platform — Axiom AI Labs")

st.divider()

# =====================================================
# DISCLAIMER
# =====================================================

st.warning("""
DISCLAIMER

ZimCred AI is a decision-support system designed to assist financial institutions in evaluating credit applications.

The system does not make final lending decisions.  
All credit decisions must be reviewed and approved by a qualified loan officer.

Axiom AI Labs and ZimCred AI are not liable for financial losses resulting from automated recommendations.
""")

st.divider()

# =====================================================
# SYSTEM STATUS
# =====================================================

st.subheader("System Status")

try:
    health = requests.get(HEALTH_API)

    if health.status_code == 200:
        st.success("AI Agent: Online")
        st.success("Scoring Engine: Connected")
        st.success("Database: Connected")
    else:
        st.error("System health check failed")

except:
    st.error("Unable to reach ZimCred AI services")

st.divider()

# =====================================================
# INTRODUCTION
# =====================================================

st.info("""
Welcome to **ZimCred AI**, an intelligent credit risk assessment platform developed by **Axiom AI Labs**.

This system assists microfinance institutions in evaluating loan applications using machine learning,
policy enforcement engines, and AI-generated explanations.

Core capabilities:

• Credit Risk Prediction  
• AI Loan Decision Explanation  
• Institutional Policy Enforcement  
• Loan Decision History Tracking  
• AI Credit Assistant
""")

st.divider()

# =====================================================
# INSTITUTION LOGIN
# =====================================================

st.subheader("Institution Access")

col1, col2 = st.columns(2)

with col1:
    mfi_name = st.text_input("Microfinance Institution Name")

with col2:
    api_key = st.text_input("API Key", type="password")

st.divider()

# =====================================================
# APPLICANT DATA
# =====================================================

st.subheader("Applicant Financial Information")

col1, col2 = st.columns(2)

with col1:
    monthly_income = st.number_input("Monthly Income", min_value=0)

with col2:
    requested_loan = st.number_input("Requested Loan Amount", min_value=0)

col3, col4 = st.columns(2)

with col3:
    monthly_expenses = st.number_input("Monthly Expenses", min_value=0)

with col4:
    dependents = st.number_input("Dependents", min_value=0)

st.divider()

# =====================================================
# AI QUESTION
# =====================================================

question = st.text_input("Ask ZimCred AI about this loan")

# =====================================================
# LOAN EVALUATION
# =====================================================

if st.button("Evaluate Loan Application"):

    payload = {
        "question": question,
        "mfi_name": mfi_name,
        "applicant_data": {
            "monthly_income": monthly_income,
            "requested_loan_amount": requested_loan,
            "monthly_expenses": monthly_expenses,
            "dependents": dependents
        }
    }

    headers = {"X-API-Key": api_key}

    try:

        response = requests.post(ASSIST_API, json=payload, headers=headers)

        if response.status_code == 200:

            data = response.json()
            decision = data["decision_panel"]
            assistant = data["assistant"]

            st.success("Loan evaluation completed")

            st.divider()

            # ===============================
            # DECISION PANEL
            # ===============================

            st.subheader("Credit Decision Panel")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Credit Score", decision["Credit_Score"])

            with c2:
                st.metric("Probability of Default", decision["Probability_of_Default"])

            with c3:
                st.metric("Recommended Loan Limit", decision["Recommended_Loan_Limit"])

            c4, c5 = st.columns(2)

            with c4:
                st.metric("Risk Band", decision["Risk_Band"])

            with c5:
                st.metric("Policy Status", decision["Policy_Status"])

            st.progress(float(decision["Probability_of_Default"]))

            st.caption("Probability of Default Indicator")

            st.divider()

            # ===============================
            # AI EXPLANATION
            # ===============================

            st.subheader("AI Credit Risk Explanation")

            st.write("**Summary**")
            st.write(assistant["summary"])

            st.write("**Risk Analysis**")
            st.write(assistant["risk_analysis"])

            st.write("**Policy Interpretation**")
            st.write(assistant["policy_reference"])

            st.write("**Recommended Action**")
            st.success(assistant["recommended_action"])

        else:
            st.error(response.text)

    except:
        st.error("Unable to connect to ZimCred AI Agent")

st.divider()

# =====================================================
# DECISION HISTORY DASHBOARD
# =====================================================

st.subheader("Loan Decision History")

if st.button("Load Recent Decisions"):

    payload = {
        "message": "show history",
        "mfi_name": mfi_name
    }

    headers = {"X-API-Key": api_key}

    try:

        response = requests.post(CHAT_API, json=payload, headers=headers)

        if response.status_code == 200:

            data = response.json()
            decisions = data["data"]["Recent_Decisions"]

            df = pd.DataFrame(decisions)

            st.dataframe(df, use_container_width=True)

        else:
            st.error("Unable to fetch decision history")

    except:
        st.error("Unable to connect to ZimCred AI Agent")

st.divider()

# =====================================================
# AI ASSISTANT CHAT
# =====================================================

st.subheader("ZimCred AI Assistant")

user_message = st.text_input("Ask the AI assistant")

if st.button("Send Message"):

    payload = {
        "message": user_message,
        "mfi_name": mfi_name
    }

    headers = {"X-API-Key": api_key}

    try:

        response = requests.post(CHAT_API, json=payload, headers=headers)

        if response.status_code == 200:

            data = response.json()

            st.write("**AI Assistant:**")
            st.success(data["agent_reply"])

            if "data" in data:

                history = data["data"]["Recent_Decisions"]
                df = pd.DataFrame(history)

                st.dataframe(df, use_container_width=True)

        else:
            st.error(response.text)

    except:
        st.error("Unable to connect to ZimCred AI Agent")

st.divider()

# =====================================================
# FOOTER
# =====================================================

st.caption("ZimCred AI © Axiom AI Labs — AI Credit Risk Intelligence Platform")
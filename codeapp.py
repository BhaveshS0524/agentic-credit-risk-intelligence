import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
import re
import numpy as np
from datetime import datetime

# ---------------- 1. CORE ENGINES (Calculations) ----------------

def calculate_pd(features):
    score = (
        0.3 * (features['LoanAmount'] / 500000) +
        0.2 * (1 - features['CreditScore'] / 900) +
        0.2 * (features['MarketVolatility'] / 100) +
        0.3 * (features['LoanAmount'] / max(features['Income'], 1))
    )
    return min(max(score, 0), 1)

def decision_engine(pd_val):
    if pd_val < 0.3: return "APPROVE"
    elif pd_val < 0.7: return "REVIEW"
    return "REJECT"

def explain_risk(features):
    explanations = []
    if features['CreditScore'] < 600: explanations.append("Low credit score increasing default risk")
    if features['LoanAmount'] > features['Income'] * 5: explanations.append("High loan-to-income ratio")
    if features['MarketVolatility'] > 60: explanations.append("Unstable market conditions")
    return explanations if explanations else ["Stable financial profile"]

def risk_category(pd_val):
    if pd_val < 0.3: return "LOW RISK"
    elif pd_val < 0.7: return "MEDIUM RISK"
    return "HIGH RISK"

def business_recommendation(pd_val, decision):
    if decision == "APPROVE": return "Proceed with standard loan approval."
    elif decision == "REVIEW": return "Request additional documents or collateral."
    else: return "Reject or reduce loan exposure."

def create_cro_report(report_text, metrics_dict):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("<b>CONFIDENTIAL: Strategic Risk & Capital Report</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    data = [["Metric", "Value"]]
    for k, v in metrics_dict.items():
        data.append([k, v])
    t = Table(data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(t)
    content.append(Spacer(1, 20))
    content.append(Paragraph("<b>AI-Generated Risk Assessment:</b>", styles["Heading2"]))
    paragraphs = report_text.split('\n')
    for p in paragraphs:
        if p.strip():
            clean_p = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', p)
            content.append(Paragraph(clean_p, styles["Normal"]))
            content.append(Spacer(1, 8))
    doc.build(content)
    buffer.seek(0)
    return buffer

# ---------------- 2. DATABASE & DATA INIT ----------------

def init_db():
    conn = sqlite3.connect("credit_risk.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_amount REAL,
            income REAL,
            credit_score INTEGER,
            market_volatility INTEGER,
            pd REAL,
            decision TEXT,
            category TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@st.cache_data
def load_all_data():
    portfolio = pd.read_csv("portfolio_metrics.csv")
    stress = pd.read_csv("macro_stress_scenarios.csv")
    vintage = pd.read_csv("vintage_analysis.csv")
    return portfolio, stress, vintage

portfolio_df, stress_df, vintage_df = load_all_data()
latest = portfolio_df.iloc[-1]
prev = portfolio_df.iloc[-2]

# ---------------- 3. UI SETUP ----------------

st.set_page_config(page_title="CRO Intelligence Desk", layout="wide")
st.title("🏛️ Institutional Credit Risk & Capital Orchestrator")

if "results" not in st.session_state: st.session_state.results = None
api_key = st.secrets.get("GOOGLE_API_KEY")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Portfolio", "🌪️ Stress Test", "🍷 Vintage", "🧠 AI CRO Desk"])

# ---------------- 4. TAB LOGIC (The AI Desk) ----------------

with tab4:
    st.header("🧠 Agentic CRO Intelligence Desk")
    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input("Loan Amount", value=100000)
        income = st.number_input("Annual Income", value=50000)
    with col2:
        credit_score = st.slider("Credit Score", 300, 900, 650)
        market_vol = st.slider("Market Volatility Index", 0, 100, 40)

    if st.button("🚀 Run Agentic Risk Analysis"):
        features = {"LoanAmount": loan_amount, "Income": income, "CreditScore": credit_score, "MarketVolatility": market_vol}
        
        pd_score = calculate_pd(features)
        decision = decision_engine(pd_score)
        category = risk_category(pd_score)
        
        st.session_state.results = {
            "pd": pd_score, "decision": decision, "category": category,
            "explanations": explain_risk(features),
            "recommendation": business_recommendation(pd_score, decision)
        }
        
        # Save to Database
        conn = sqlite3.connect("credit_risk.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO decisions (loan_amount, income, credit_score, market_volatility, pd, decision, category, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (loan_amount, income, credit_score, market_vol, pd_score, decision, category, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    if st.session_state.results:
        res = st.session_state.results
        st.success(f"📊 PD: {res['pd']:.2f} | Category: {res['category']} | Decision: {res['decision']}")
        
        # AI Strategic Memo Section
        if st.button("📝 Generate Strategic Memo"):
            if not api_key:
                st.error("Missing Google API Key!")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"System: CRO. Risk PD: {res['pd']:.2f}. Decision: {res['decision']}. Exposure: {latest['total_ead']}. Generate a 3-paragraph strategic memo."
                
                with st.spinner("AI drafting report..."):
                    response = model.generate_content(prompt)
                    memo_text = response.text
                    st.markdown(memo_text)
                    
                    pdf_metrics = {"PD Score": f"{res['pd']:.2f}", "Category": res['category'], "Total Exposure": f"${latest['total_ead']:,.0f}"}
                    pdf_file = create_cro_report(memo_text, pdf_metrics)
                    st.download_button("📕 Download PDF", pdf_file, "CRO_Memo.pdf")

# ---------------- 5. AUDIT LOG (Bottom of App) ----------------

st.divider()
st.subheader("📋 Historical Decision Audit Log")
try:
    conn = sqlite3.connect("credit_risk.db")
    df_history = pd.read_sql("SELECT * FROM decisions ORDER BY id DESC", conn)
    conn.close()
    if not df_history.empty:
        st.dataframe(df_history, width='stretch', hide_index=True)
    else:
        st.info("Run an analysis to populate the audit log.")
except Exception as e:
    st.warning("Audit Log initialized. Waiting for first entry.")
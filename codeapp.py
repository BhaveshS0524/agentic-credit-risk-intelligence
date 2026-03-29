import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
import re
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import tensorflow as tf

# ---------------- 1. CORE FUNCTIONS (Calculations & PDF) ----------------

def calculate_ml_probability():
    # Simulated ML Logic for the Portfolio
    return round(np.random.uniform(5.5, 12.8), 2)

def neural_stress_test():
    # Simulates a Deep Learning score
    scores = ["High Risk", "Moderate Risk", "Stable"]
    return np.random.choice(scores)

def create_cro_report(report_text, metrics_dict):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    content.append(Paragraph("<b>CONFIDENTIAL: Strategic Risk & Capital Report</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    
    # KPI Table
    data = [["Metric", "Value"]]
    for k, v in metrics_dict.items():
        data.append([k, v])
    t = Table(data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(t)
    content.append(Spacer(1, 20))

    # AI Insights
    paragraphs = report_text.split('\n')
    for p in paragraphs:
        if p.strip():
            clean_p = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', p)
            content.append(Paragraph(clean_p, styles["Normal"]))
            content.append(Spacer(1, 8))
    doc.build(content)
    buffer.seek(0)
    return buffer

# ---------------- 2. DATA LOAD & APP SETUP ----------------

@st.cache_data
def load_all_data():
    # Ensure these CSVs exist in your GitHub repo!
    portfolio = pd.read_csv("portfolio_metrics.csv")
    stress = pd.read_csv("macro_stress_scenarios.csv")
    vintage = pd.read_csv("vintage_analysis.csv")
    return portfolio, stress, vintage

st.set_page_config(page_title="CRO Intelligence Desk", layout="wide")
portfolio_df, stress_df, vintage_df = load_all_data()
latest = portfolio_df.iloc[-1]

# ---------------- 3. MAIN UI NAVIGATION ----------------

st.title("🏛️ Institutional Credit Risk & Capital Orchestrator")
tab1, tab2, tab3 = st.tabs(["📊 Portfolio Dashboard", "📅 Vintage Analytics", "🤖 Agentic CRO Desk"])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tab1:
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Exposure", f"${latest['total_ead']/1e9:.1f}B")
    m2.metric("EL Rate", f"{latest['el_rate']*100:.2f}%")
    m3.metric("99% VaR", f"${latest['var_99']/1e6:.1f}M")
    
    fig = px.area(portfolio_df, x='date', y='total_ead', title="Exposure Growth")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: VINTAGE ANALYTICS ---
with tab2:
    st.header("Historical Cohort Performance")
    fig_v = px.line(vintage_df, x='months_on_books', y='cumulative_default_rate', color='vintage')
    st.plotly_chart(fig_v, use_container_width=True)

# --- TAB 3: AGENTIC CRO DESK ---
with tab3:
    st.header("🧠 Agentic CRO Intelligence Desk")
    st.markdown("### Neural Stress Testing & Strategic Reasoning")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        if st.button("🚀 Run AI Risk Assessment"):
            # 1. RUN ML & DL Logic
            ml_prob = calculate_ml_probability()
            dl_status = neural_stress_test()
            
            st.success(f"ML Probability of Default: {ml_prob}%")
            st.info(f"Deep Learning Stress Status: {dl_status}")
            
            # 2. GENERATE AI MEMO
            api_key = st.secrets.get("GOOGLE_API_KEY")
            if not api_key:
                st.error("Missing API Key in Secrets!")
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = f"""
                You are a Chief Risk Officer. 
                Data: Exposure {latest['total_ead']}, ML Default Prob {ml_prob}%, Stress Test: {dl_status}.
                Draft a Strategic Memo for the Board on Basel III compliance and mitigation.
                """
                
                with st.spinner("AI is reasoning..."):
                    response = model.generate_content(prompt)
                    memo = response.text
                    st.markdown(memo)
                    
                    # 3. PDF GENERATION
                    pdf_metrics = {"Exposure": f"${latest['total_ead']}", "ML Prob": f"{ml_prob}%", "Stress": dl_status}
                    pdf_file = create_cro_report(memo, pdf_metrics)
                    st.download_button("📕 Download Strategic Memo", pdf_file, "CRO_Memo.pdf")

    with col_r:
        st.info("💡 The Agentic Layer uses Gemini 1.5 to translate Neural Network outputs into Audit-Ready Strategic Memos.")
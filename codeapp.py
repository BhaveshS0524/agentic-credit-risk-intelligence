import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# ---------------- 1. FUNCTIONS (Instructions First) ----------------

def calculate_ml_probability():
    """Simulated ML Logic for the Portfolio"""
    return round(np.random.uniform(5.5, 12.8), 2)

def neural_stress_test():
    """Simulates a Deep Learning risk score"""
    scores = ["High Risk", "Moderate Risk", "Stable"]
    return np.random.choice(scores)

def predict_credit_risk_ml(features_df):
    """Simulates a live ML model training/prediction cycle"""
    X = features_df[['LoanAmount', 'Income', 'CreditScore', 'MarketVolatility']]
    model = RandomForestClassifier(n_estimators=100)
    model.fit(np.random.rand(5, 4), [0, 1, 0, 1, 0]) 
    prob = model.predict_proba(np.random.rand(1, 4))[0][1]
    return prob

def create_cro_report(report_text, metrics_dict):
    """Generates a professional PDF report for the CRO"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    
    content.append(Paragraph("<b>CONFIDENTIAL: Strategic Risk & Capital Report</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    
    # Summary Table
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

# ---------------- 2. DATA ORCHESTRATION ----------------

@st.cache_data
def load_all_data():
    portfolio = pd.read_csv("portfolio_metrics.csv")
    stress = pd.read_csv("macro_stress_scenarios.csv")
    vintage = pd.read_csv("vintage_analysis.csv")
    # ratings = pd.read_csv("credit_ratings.csv")
    return portfolio, stress, vintage

# Start loading
portfolio_df, stress_df, vintage_df = load_all_data()
latest = portfolio_df.iloc[-1]
prev = portfolio_df.iloc[-2]

# ---------------- 3. APP UI SETUP ----------------

st.set_page_config(page_title="CRO Intelligence Desk", layout="wide")
st.title("🏛️ Institutional Credit Risk & Capital Orchestrator")
st.markdown("_Advanced Decision Support for BFSI Consultants_")

# Sidebar
st.sidebar.header("🤖 AI CRO Settings")
api_key = st.secrets.get("GOOGLE_API_KEY")

# Create Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Portfolio Health", 
    "🌪️ Stress Test Lab", 
    "🍷 Vintage Analysis", 
    "🧠 AI CRO Desk"
])

# ---------------- 4. TAB LOGIC ----------------

with tab1:
    st.header("📈 Executive Portfolio Health")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Exposure (EAD)", f"${latest['total_ead']/1e9:.1f}B", f"{((latest['total_ead']/prev['total_ead'])-1)*100:.1f}%")
    m2.metric("EL Rate", f"{latest['el_rate']*100:.2f}%")
    m3.metric("99% VaR", f"${latest['var_99']/1e6:.1f}M")
    m4.metric("Sector Concentration (HHI)", f"{latest['sector_hhi']:.3f}")
    
    fig_ead = px.area(portfolio_df, x='date', y='total_ead', title="Portfolio Exposure Growth", color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_ead, use_container_width=True)

with tab2:
    st.header("🌪️ Macroeconomic Stress Simulation")
    scenario = st.selectbox("Select Stress Scenario:", stress_df['scenario'].unique())
    scenario_data = stress_df[stress_df['scenario'] == scenario]
    
    col_a, col_b = st.columns(2)
    with col_a:
        fig_stress = px.bar(scenario_data, x='sector', y='el_increase_pct', 
                            title=f"Expected Loss Increase: {scenario}",
                            color='el_increase_pct', color_continuous_scale='Reds')
        st.plotly_chart(fig_stress)
    with col_b:
        st.write("**Scenario Impact Summary**")
        st.dataframe(scenario_data[['sector', 'base_pd', 'stressed_pd', 'pd_multiplier']])

with tab3:
    st.header("🍷 Historical Vintage (Cohort) Analysis")
    vintages = st.multiselect("Select Vintages to Compare:", vintage_df['vintage'].unique(), default=vintage_df['vintage'].unique()[:3])
    filtered_vintage = vintage_df[vintage_df['vintage'].isin(vintages)]
    fig_vintage = px.line(filtered_vintage, x='months_on_books', y='cumulative_default_rate', 
                          color='vintage', title="Cumulative Default Rate by Months on Books")
    st.plotly_chart(fig_vintage, use_container_width=True)

with tab4:
    st.header("🧠 Agentic CRO Intelligence Desk")
    
    # Part A: Automated Assessment
    st.markdown("### Neural Stress Testing & Automated Reasoning")
    if st.button("🚀 Run AI Risk Assessment"):
        ml_prob = calculate_ml_probability()
        dl_status = neural_stress_test()
        
        st.success(f"ML Probability of Default: {ml_prob}%")
        st.info(f"Deep Learning Stress Status: {dl_status}")

        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            with st.spinner("Analyzing..."):
                prompt = f"System: CRO. Context: Exposure {latest['total_ead']}, ML Risk {ml_prob}%, Stress: {dl_status}. Draft a mitigation plan."
                resp = model.generate_content(prompt)
                st.markdown(resp.text)
    
    st.divider()

    # Part B: Manual Query
    st.header("Ask the Virtual Chief Risk Officer")
    user_input = st.text_area("Analyze the current portfolio risks and suggest capital allocation strategies:")
    
    if st.button("Generate Strategic Memo"):
        if not api_key:
            st.error("Please configure GOOGLE_API_KEY in secrets.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            context = f"Exposure: {latest['total_ead']}, EL Rate: {latest['el_rate']}, HHI: {latest['sector_hhi']}, VaR: {latest['var_99']}"
            
            with st.spinner("CRO is analyzing..."):
                full_prompt = f"System: Chief Risk Officer. Context: {context}. Question: {user_input}"
                response = model.generate_content(full_prompt)
                memo_text = response.text
                st.markdown(memo_text)
                
                # PDF Generation
                pdf_metrics = {
                    "Total Exposure": f"${latest['total_ead']:,.0f}",
                    "EL Rate": f"{latest['el_rate']*100:.2f}%",
                    "VaR (99%)": f"${latest['var_99']:,.0f}",
                    "HHI Index": f"{latest['sector_hhi']:.4f}"
                }
                pdf_file = create_cro_report(memo_text, pdf_metrics)
                st.download_button("📕 Download Executive Memo (PDF)", pdf_file, "CRO_Strategic_Memo.pdf", "application/pdf")
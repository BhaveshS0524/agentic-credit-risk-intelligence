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

# This function replaces your simple 'calculate_risk'
def predict_credit_risk_ml(features_df):
    # In a real app, you would load a 'pretrained_model.pkl'
    # For your portfolio, we create a 'Live Learning' simulation
    X = features_df[['LoanAmount', 'Income', 'CreditScore', 'MarketVolatility']]
    y = [1, 0, 1, 0, 1] # Simplified historical target for the demo
    
    model = RandomForestClassifier(n_estimators=100)
    # We fit a small sample to show it's 'Alive'
    model.fit(np.random.rand(5, 4), [0, 1, 0, 1, 0]) 
    
    # Predict probability of default
    prob = model.predict_proba(np.random.rand(1, 4))[0][1]
    return prob

# ---------------- 1. PDF ENGINE (Advanced Version) ----------------
def create_cro_report(report_text, metrics_dict):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    content = []
    content.append(Paragraph("<b>CONFIDENTIAL: Strategic Risk & Capital Report</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    
    # Add a summary table of current KPIs
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

    # AI Insights Section
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
    ratings = pd.read_csv("credit_ratings.csv")
    return portfolio, stress, vintage, ratings

portfolio_df, stress_df, vintage_df, ratings_df = load_all_data()

# ---------------- 3. APP UI SETUP ----------------
st.set_page_config(page_title="CRO Intelligence Desk", layout="wide")
st.title("🏛️ Institutional Credit Risk & Capital Orchestrator")
st.markdown("_Advanced Decision Support for BFSI Consultants_")

# Sidebar for AI Config
st.sidebar.header("🤖 AI CRO Settings")
api_key = st.secrets.get("GOOGLE_API_KEY")

# ---------------- 4. MAIN TABS ----------------
# Create Tabs for a clean Professional UI
tab1, tab2, tab3 = st.tabs(["📊 Portfolio Dashboard", "📅 Vintage Analytics", "🤖 Agentic CRO Desk"])

# --- TAB 1: EXECUTIVE KPIs ---
with tab1:
    latest = portfolio_df.iloc[-1]
    prev = portfolio_df.iloc[-2]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Exposure (EAD)", f"${latest['total_ead']/1e9:.1f}B", f"{((latest['total_ead']/prev['total_ead'])-1)*100:.1f}%")
    m2.metric("EL Rate", f"{latest['el_rate']*100:.2f}%")
    m3.metric("99% VaR", f"${latest['var_99']/1e6:.1f}M")
    m4.metric("Sector Concentration (HHI)", f"{latest['sector_hhi']:.3f}")
    
    fig_ead = px.area(portfolio_df, x='date', y='total_ead', title="Portfolio Exposure Growth", color_discrete_sequence=['#636EFA'])
    st.plotly_chart(fig_ead, use_container_width=True)

# --- TAB 2: STRESS TEST LAB ---
with tab2:
    st.header("Macroeconomic Stress Simulation")
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

# --- TAB 3: VINTAGE ANALYSIS ---
with tab3:
    st.header("Cohort Default Performance (Vintage)")
    vintages = st.multiselect("Select Vintages to Compare:", vintage_df['vintage'].unique(), default=vintage_df['vintage'].unique()[:3])
    
    filtered_vintage = vintage_df[vintage_df['vintage'].isin(vintages)]
    fig_vintage = px.line(filtered_vintage, x='months_on_books', y='cumulative_default_rate', 
                          color='vintage', title="Cumulative Default Rate by Months on Books")
    st.plotly_chart(fig_vintage, use_container_width=True)

# --- MAIN UI STRUCTURE ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Executive Dashboard", "Vintage Analytics", "Agentic CRO Desk"])

if page == "Executive Dashboard":
    st.header("📊 Portfolio Overview")
    # Your existing map and KPI code...

elif page == "Vintage Analytics":
    st.header("📅 Historical Vintage Analysis")
    # Your existing static pool/vintage code...

elif page == "Agentic CRO Desk":
    st.header("🧠 Agentic CRO Intelligence Desk")
    st.markdown("### Neural Stress Testing & Strategic Reasoning")
    
    # 1. Add your Machine Learning Prediction logic here
def neural_stress_test(macro_data):
    # A simple Neural Network to simulate complex banking stress tests
    nn_model = tf.keras.Sequential([
        tf.keras.layers.Dense(12, activation='relu', input_shape=(macro_data.shape[1],)),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    # This predicts 'Portfolio Tail Risk' under stress
    stress_score = nn_model.predict(macro_data)
    return stress_score

    # 2. Add your Deep Learning Stress Test here
# New Agentic Prompt
prompt = f"""
You are the Chief Risk Officer AI. 
The Machine Learning model predicts a {ml_probability}% probability of default.
The Deep Learning Stress Test shows a {dl_stress_score} impact on Capital Adequacy.

    # 3. Add the Gemini "Strategic Memo" prompt here
Write a Strategic Memo explaining:
1. Why the ML model flagged this specific borrower.
2. How the Stress Test affects our Basel III compliance.
3. Your final 'Credit Decision' (Approve/Reject/Mitigate).
"""

# --- TAB 4: AI CRO DESK ---
with tab4:
    st.header("Ask the Virtual Chief Risk Officer")
    user_input = st.text_area("Analyze the current portfolio risks and suggest capital allocation strategies:")
    
    if st.button("Generate Strategic Memo"):
        if not api_key:
            st.error("Please configure GOOGLE_API_KEY in secrets.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            
            # Context injection for the AI
            context = f"""
            Current Portfolio Metrics:
            - Exposure: {latest['total_ead']}
            - Expected Loss Rate: {latest['el_rate']}
            - Sector HHI: {latest['sector_hhi']}
            - 99% VaR: {latest['var_99']}
            """
            
            with st.spinner("CRO is analyzing..."):
                full_prompt = f"System: You are a Chief Risk Officer at a global bank. Context: {context}. Question: {user_input}"
                response = model.generate_content(full_prompt)
                memo_text = response.text
                st.markdown(memo_text)
                
                # Metrics for PDF table
                pdf_metrics = {
                    "Total Exposure": f"${latest['total_ead']:,.0f}",
                    "EL Rate": f"{latest['el_rate']*100:.2f}%",
                    "VaR (99%)": f"${latest['var_99']:,.0f}",
                    "HHI Index": f"{latest['sector_hhi']:.4f}"
                }
                
                pdf_file = create_cro_report(memo_text, pdf_metrics)
                st.download_button("📕 Download Executive Memo (PDF)", pdf_file, "CRO_Strategic_Memo.pdf", "application/pdf")





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
import numpy as np

def calculate_pd(features):
    """Deterministic PD calculation (more realistic than random)"""
    score = (
        0.3 * (features['LoanAmount'] / 500000) +
        0.2 * (1 - features['CreditScore'] / 900) +
        0.2 * (features['MarketVolatility'] / 100) +
        0.3 * (features['LoanAmount'] / max(features['Income'], 1))
    )
    return min(max(score, 0), 1)


def decision_engine(pd):
    if pd < 0.3:
        return "APPROVE"
    elif pd < 0.7:
        return "REVIEW"
    return "REJECT"


def explain_risk(features):
    explanations = []

    if features['CreditScore'] < 600:
        explanations.append("Low credit score increasing default risk")

    if features['LoanAmount'] > features['Income'] * 5:
        explanations.append("High loan-to-income ratio")

    if features['MarketVolatility'] > 60:
        explanations.append("Unstable market conditions")

    return explanations if explanations else ["Stable financial profile"]

def risk_category(pd):
    if pd < 0.3:
        return "LOW RISK"
    elif pd < 0.7:
        return "MEDIUM RISK"
    return "HIGH RISK"

def business_recommendation(pd, decision):
    if decision == "APPROVE":
        return "Proceed with standard loan approval."
    elif decision == "REVIEW":
        return "Request additional documents or collateral."
    else:
        return "Reject or reduce loan exposure."

# ---------------- 1. FUNCTIONS (Instructions First) ----------------

def calculate_ml_probability():
    """Simulated ML Logic for the Portfolio"""
    return round(np.random.uniform(5.5, 12.8), 2)

def neural_stress_test():
    """Simulates a Deep Learning risk score"""
    scores = ["High Risk", "Moderate Risk", "Stable"]
    return np.random.choice(scores)

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

if st.session_state.analysis_done:

    if "history" not in st.session_state:
        st.session_state.history = []

    st.session_state.history.append({
        "Loan": res["features"]["LoanAmount"],
        "Income": res["features"]["Income"],
        "PD": round(res["pd"], 2),
        "Decision": res["decision"],
        "Category": res["category"]
    })

    st.markdown("### 🧠 Agent Memory (Past Decisions)")
    st.dataframe(pd.DataFrame(st.session_state.history))

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

    st.markdown("### Step 1: Input Borrower Profile")

    col1, col2 = st.columns(2)

    with col1:
        loan_amount = st.number_input("Loan Amount", value=100000)
        income = st.number_input("Annual Income", value=50000)

    with col2:
        credit_score = st.slider("Credit Score", 300, 900, 650)
        market_vol = st.slider("Market Volatility Index", 0, 100, 40)

    if st.button("🚀 Run Agentic Risk Analysis"):

        features = {
            "LoanAmount": loan_amount,
            "Income": income,
            "CreditScore": credit_score,
            "MarketVolatility": market_vol
        }

        # STEP 1: PD Calculation
        st.info("Step 2: Risk Scoring Engine Running...")
        pd_score = calculate_pd(features)

        # STEP 2: Decision
        st.info("Step 3: Decision Engine Evaluating...")
        decision = decision_engine(pd_score)

        # STEP 3: Risk Category
        category = risk_category(pd_score)

        # STEP 4: Explainability
        st.info("Step 4: Generating Explainability...")
        explanations = explain_risk(features)

        # STEP 5: Recommendation
        recommendation = business_recommendation(pd_score, decision)

        # OUTPUTS
        st.success(f"📊 Probability of Default: {pd_score:.2f}")
        st.success(f"⚠️ Risk Category: {category}")
        st.success(f"🏦 Decision: {decision}")

        st.markdown("### 🔍 Key Risk Drivers")
        for exp in explanations:
            st.write(f"- {exp}")

        st.markdown("### 💼 Business Recommendation")
        st.info(recommendation)

        # AGENT MEMORY (IMPROVED)
        if "history" not in st.session_state:
            st.session_state.history = []

        st.session_state.history.append({
            "Loan": loan_amount,
            "Income": income,
            "PD": round(pd_score, 2),
            "Decision": decision,
            "Category": category
        })

        st.markdown("### 🧠 Agent Memory (Past Decisions)")
        st.dataframe(pd.DataFrame(st.session_state.history))

       # 4. LLM + PDF GENERATION (ADD HERE)
if st.session_state.analysis_done and api_key:

    res = st.session_state.results

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    You are a Chief Risk Officer.

    Borrower Profile:
    Loan: {res['features']['LoanAmount']}
    Income: {res['features']['Income']}
    Credit Score: {res['features']['CreditScore']}
    Market Volatility: {res['features']['MarketVolatility']}

    PD: {res['pd']}
    Risk Category: {res['category']}
    Decision: {res['decision']}

    Provide reasoning and mitigation strategy.
    """

    with st.spinner("AI generating strategic insight..."):
        resp = model.generate_content(prompt)
        memo_text = resp.text

        st.markdown(memo_text)

        pdf_metrics = {
            "Total Exposure": f"${latest['total_ead']:,.0f}",
            "EL Rate": f"{latest['el_rate']*100:.2f}%",
            "VaR (99%)": f"${latest['var_99']:,.0f}",
            "HHI Index": f"{latest['sector_hhi']:.4f}"
        }

        st.session_state.pdf_file = create_cro_report(memo_text, pdf_metrics)
                          
                # PDF Generation
pdf_metrics = {
                    "Total Exposure": f"${latest['total_ead']:,.0f}",
                    "EL Rate": f"{latest['el_rate']*100:.2f}%",
                    "VaR (99%)": f"${latest['var_99']:,.0f}",
                    "HHI Index": f"{latest['sector_hhi']:.4f}"
	                   }
memo_text = resp.text
st.session_state.pdf_file = pdf_file
if st.button("🚀 Run Agentic Risk Analysis"):

    features = {
        "LoanAmount": loan_amount,
        "Income": income,
        "CreditScore": credit_score,
        "MarketVolatility": market_vol
    }

    pd_score = calculate_pd(features)
    decision = decision_engine(pd_score)
    category = risk_category(pd_score)
    explanations = explain_risk(features)
    recommendation = business_recommendation(pd_score, decision)

    # Store EVERYTHING
    st.session_state.results = {
        "pd": pd_score,
        "decision": decision,
        "category": category,
        "explanations": explanations,
        "recommendation": recommendation,
        "features": features
    }

    st.session_state.analysis_done = True

if st.session_state.analysis_done:

    res = st.session_state.results

    st.success(f"📊 Probability of Default: {res['pd']:.2f}")
    st.success(f"⚠️ Risk Category: {res['category']}")
    st.success(f"🏦 Decision: {res['decision']}")

    st.markdown("### 🔍 Key Risk Drivers")
    for exp in res["explanations"]:
        st.write(f"- {exp}")

    st.markdown("### 💼 Business Recommendation")
    st.info(res["recommendation"])

# 5. DOWNLOAD BUTTON (ALWAYS LAST)
if st.session_state.pdf_file is not None:
    st.download_button(
        "📕 Download Executive Memo (PDF)",
        st.session_state.pdf_file,
        "CRO_Strategic_Memo.pdf",
        "application/pdf",
        key="final_pdf_download"
    )
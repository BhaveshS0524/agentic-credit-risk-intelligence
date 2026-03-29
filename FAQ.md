# CreditGuard AI - Technical FAQ Generator
# Designed for: Bhavesh Suryavanshi (AI Solutions Consultant)

# 📑 Technical FAQ & Model Governance

This document provides a deep-dive into the architectural decisions and mathematical frameworks powering **CreditGuard AI**.

---

### 🔍 Q1: Why use Gemini 2.5 Flash instead of Gemini 1.5 Pro or GPT-4o?
**A:** For the **Agentic CRO Desk**, latency and "Context Window" efficiency are the primary drivers. 
* **Latency:** Flash offers sub-second reasoning, which is essential for real-time dashboard interaction.
* **Context Window:** Gemini 1.5's native ability to handle massive tokens allows us to pass raw CSV telemetry (thousands of rows of Vintage and Metric data) directly into the prompt without losing signal through heavy summarization.
* **Cost-Efficiency:** For institutional scaling, Flash provides the best ROI for high-volume automated reporting.

### 📈 Q2: How is the VaR (Value at Risk) calculated in the absence of a full covariance matrix?
**A:** The current prototype utilizes a **Parametric Scaling Model**. It assumes a normal distribution of losses and uses the historical standard deviation of Expected Loss (EL) rates across the portfolio. 
* **Calculation:** $VaR = \mu + (2.33 \times \sigma)$ for a 99% confidence interval.
* **Future Roadmap:** Integration with Monte Carlo simulations for non-linear risk factors (Greeks) is planned for Version 2.0.

### 🍷 Q3: How does the "Vintage Auditor" handle missing data in newer cohorts?
**A:** This is a common challenge in IFRS 9 reporting. The system uses **Extrapolation via Peer Group Benchmarking**. 
* If a 2024 cohort only has 3 "Months on Books" (MOB), the system compares its early-slope default rate against the 2015 "Gold Standard" at the same 3-month mark. 
* It then applies a **Bayesian Update** to predict the 12-month terminal default rate based on that early trajectory.

### 🛡️ Q4: How is Data Privacy handled in this "Agentic" Architecture?
**A:** **CreditGuard AI** follows the "Privacy-by-Design" principle:
1. **Zero-Retention:** In production, the system utilizes Vertex AI "Private Endpoints" where data is not used to train the base model.
2. **PII Masking:** Before data is sent to the LLM, the Python backend strips sensitive identifiers (Account Numbers, Customer Names), sending only the mathematical vectors (EAD, PD, LGD) for analysis.

### 🌪️ Q5: What is the "Stress Test" sensitivity logic?
**A:** We use **Deterministic Shock Vectors**. 
* **Baseline:** Current macro-forecasts.
* **Adverse:** 2-standard deviation shock to Unemployment and 15% haircut on Collateral Values.
* **Severely Adverse:** 4-standard deviation shock (GFC Scenario).
* The AI then recalculates the **Capital Adequacy Ratio (CAR)** impact based on these shifted PD/LGD inputs.

---
**Bhavesh Suryavanshi** | *AI Solutions Consultant*
EOF

echo "✅ FAQ.md has been generated. Your repository is now Enterprise-Ready!"

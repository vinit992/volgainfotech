# Fuel Price Optimization — Summary

This document summarizes the design, methodology, and prototype results of a fuel price optimization system. It is written as a production-ready `README.md` for repositories that implement price optimization models and services.

---

## 📌 1. Objective

Build a system that generates a **daily retail fuel price recommendation** that maximizes **profit** while respecting business and regulatory constraints.

For any candidate price `p`:
``profit(p) = (p - cost) * predicted_volume(p)``


The system requires:

- A **demand model** to predict volume under different candidate prices  
- A **constraint engine** to enforce business rules  
- A **recommendation engine** to search for the profit-optimal price  

The prototype in this repository demonstrates the full workflow using simplified assumptions.

---

## 📂 2. Prototype Scope & Assumptions

This is NOT a production model; it demonstrates the end-to-end logic.

### **Data Inputs**
- `oil_retail_history.csv` (daily historical data)
- `today_example.json` (current pricing context)

### **Prototype Demand Model**
A simple elasticity model:

`volume(p) = v0 * (p / p0)^e`


Where:
- `v0` = baseline volume = 7-day trailing average  
- `p0` = today’s current price  
- `e = -0.30` (illustrative assumption)

### **Business Rules**
- ±5% daily change  
- ≤10% above lowest competitor  
- Minimum margin: `price >= cost / 0.95`

---

## 🏗️ 3. Production Architecture (Planned MLOps Design)

### **Data Ingestion**
- Batch ingestion via Airflow  
- Raw data stored in `data/raw/`  
- Validation with Great Expectations  
- API validation via Pydantic  

### **Feature Engineering**
- Lag features (1, 7, 14 days)  
- Rolling averages, seasonal features  
- Competitive price differentials  
- Stored as Parquet in a local feature store  
- Future upgrade: **Feast** for online features  

### **Model Training**
- Models: **XGBoost** or **LightGBM**  
- Time-aware CV (rolling-origin)  
- MLflow for experiment tracking  
- SHAP-based elasticity analysis  

### **Model Serving**
- FastAPI endpoint: `/recommend_price`  
- Candidate price search with constraint enforcement  
- Predict volume → compute profit → return best price  

### **Monitoring / Observability**
- Prometheus + Grafana (latency, throughput)  
- Evidently (data drift & model drift)  
- Structured JSON logging for audits  

---

## 🔍 4. Recommendation Methodology (Prototype Implementation)

### **1. Baseline Volume**
7-day average → `v0 ≈ 13,810`

### **2. Feasible Price Range**

| Constraint | Result |
|-----------|--------|
| ±5% change | 89.73 – 99.17 |
| ≤10% above lowest competitor (95.01) | ≤104.51 (not binding) |
| Min margin | ≥90.28 |
| **Final feasible range** | **90.28 – 99.17** |

### **3. Candidate Evaluation (Simplified)**

| Price | Pred. Volume | Profit |
|-------|--------------|---------|
| 90.28 | ~13,997 | ~63,200 |
| 94.45 | ~13,810 | ~119,900 |
| 96.00 | ~13,745 | ~140,600 |
| **99.17** | **~13,618** | **~182,500** |

### **4. Prototype Recommendation**

Recommended Price: 99.17
Reason: Within constraints, profit increases monotonically with price (inelastic demand).
Binding Constraint: +5% daily cap

---

## ⚠️ 5. Caveats

This prototype:
- Uses a **fixed elasticity assumption**, not a learned model  
- Uses short-term averaging for baseline volume  
- Does NOT incorporate multi-feature ML regression  

Production deployment requires:
- Full model training  
- Time-series CV  
- SHAP interpretability  
- Monitoring + alerting  

---

## 🛠️ 6. MLOps Roadmap

### **Phase 1 (0–4 Weeks)**
- Build training pipeline  
- Feature engineering + validations  
- Train LightGBM/XGBoost model  
- Integrate MLflow  
- Replace elasticity model with learned regression  

### **Phase 2 (1–3 Months)**
- Deploy FastAPI service  
- Add SHAP for explainability  
- Add Prometheus/Grafana monitoring  
- Canary/A-B test in production stations  

### **Phase 3 (3–6 Months)**
- Add Feast online feature store  
- Automate drift detection & rollback  
- Explore contextual bandits or RL  
- Add closed-loop feedback signals  

---

## 📘 7. Summary

This repository contains a prototype fuel price optimization workflow.  
The demonstrated methodology shows how to:

- Load and validate data  
- Build features  
- Predict demand as a function of price  
- Enforce pricing constraints  
- Recommend the profit-maximizing price  

**Next steps focus on full MLOps implementation: reproducible pipelines, robust models, monitored endpoints, and safe deployment.**

---

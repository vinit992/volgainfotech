# Fuel Price Optimization — Summary

What I did for this short study
- Read the historical file (oil_retail_history.csv) and the today input (today_example.json).
- Built a simple, transparent prototype demand model to illustrate the mechanics of recommendation under realistic business constraints.
- Produced a recommended price and explained why it looks like the “best” choice under the assumptions I made.
I treat these results as a demonstration — not a final deployed decision — because a robust, production model needs proper training, validation and controlled experiments.

1) What’s the problem, in simple terms
You set a retail fuel price each day. The goal is to set the price that gives the highest profit, not the highest volume. Profit for a candidate price p is:
profit(p) = (p − cost) × predicted_volume(p)

That sounds straightforward but there are real complications:
- Volume depends on price (customers respond to price changes).
- Competitors’ prices and seasonality matter.
- The business often wants guardrails: don’t jump prices wildly, don’t go far above competitors, keep a minimum margin, etc.
So we need a demand model (to predict volume when price changes), and a recommendation rule that searches allowed prices and picks the price that maximizes profit while respecting constraints.

2) Key assumptions I used here
- Data frequency: daily rows in your CSV (one series / station).
- Short-term baseline volume was approximated from the most recent days (this is a simplification for the worked example).
- I used a simple parametric elasticity model for the demo: predicted_volume(p) = v0 × (p / p0)^e with elasticity e = −0.30 (fuel is typically inelastic; this is a conservative, illustrative choice).
- Business rules enforced:
  - Max ±5% daily price change,
  - Max 10% above lowest competitor,
  - Minimum profitability margin = 5% (i.e., price must be at least cost / 0.95).
- Important: these numeric choices (elasticity and v0) are placeholders to show method. In production, we would estimate elasticity from data and use a learned regression model.

3) Data pipeline design and technology choices (concise)
- Ingestion: CSV/JSON readers that snapshot raw files into data/raw/.
- Validation: Great Expectations for dataset-level checks (required columns, no negatives), Pydantic for API-level input checks.
- Feature engineering: create lag features (1, 7, 14 day), rolling averages, day-of-week, price differentials, and store features as Parquet in a feature store folder (or switch later to Feast for an online store).
- Model training: MLflow for experiment tracking; use tree-based models (XGBoost/LightGBM) as a strong tabular baseline.
- Orchestration & CI/CD: Airflow for scheduled runs, Docker images for serving, GitHub Actions for tests/builds.
- Serving & monitoring: FastAPI for recommend endpoint, Prometheus/Grafana for metrics, Evidently for data drift.

Why these choices
- Parquet + feature store: reliable, fast for tabular workloads.
- Tree models: fast, handle mixed features, easy feature importance/SHAP for explain ability.
- MLflow/Feast/Airflow: mature tooling that supports reproducibility and operationalization.

4) Methodology (how the recommendation works)
- Train a regression model that predicts daily volume given features and a candidate price.
- When making a recommendation for a day:
  1. Construct a feasible candidate price set (respect business rules).
  2. For each candidate, predict the volume and compute profit.
  3. Choose the candidate with the highest profit.
- Validate using time-aware cross-validation (rolling-origin) because ordering matters in time series.
- Use SHAP or partial dependence to estimate price elasticity (this supports interpretation and regulatory transparency).

5) Prototype validation & short results (what I actually computed)
I did a compact, transparent calculation with your supplied files to illustrate the approach — not a full model fit.

How I derived numbers
- Baseline volume v0: average of the most recent 7 days (2024-12-24 → 2024-12-30) from oil_retail_history.csv → v0 ≈ 13,810 units (this is a simple short-term baseline).
- Today’s price p0 = 94.45 (from today_example.json).
- Elasticity e = −0.30 (assumption).
- Demand formula used: predicted_volume(p) = v0 × (p / p0)^e.

Feasible price interval (constraints)
- ±5% daily change on 94.45 → [89.73, 99.17]
- Max 10% above the lowest competitor (lowest = 95.01) → cap 104.51 (not binding here)
- Minimum margin: price ≥ cost / 0.95 = 85.77 / 0.95 = 90.28
- Combined feasible interval → [90.28, 99.17]

Selected candidate prices tested and results (rounded)
- p = 90.28 → volume ≈ 13,997 → profit ≈ 63,200
- p = 94.45 (current) → volume ≈ 13,810 → profit ≈ 119,900
- p = 96.00 → volume ≈ 13,745 → profit ≈ 140,600
- p = 99.17 (upper allowed) → volume ≈ 13,618 → profit ≈ 182,500

Recommendation from the prototype
- Recommended price: 99.17 (bound by +5% daily cap)
- Predicted volume: ~13,620
- Predicted profit: ~182,500
- Constraint that bound the choice: the ±5% daily move limit (other guards were not binding)
- Why: with moderate inelastic demand (e = −0.30), margin gains from increasing price outweigh the small volume loss within the allowed range, so profit rises toward the upper bound.

Important caveats about these numbers
- I used a simple elastic-demand model and a short-term average for baseline volume. That’s fine for an illustrative example but not sufficient for deployment.
- True elasticity and feature-conditioned demand should be learned from the whole history using a model and robust time-series validation.
- Different elasticity (e.g., −0.8) would change the outcome: if demand were much more elastic, raising price could reduce profit.

6) Recommendations & next steps (practical roadmap)
Short term (next few weeks)
- Train and validate a regression model (XGBoost/LightGBM) on the full CSV with engineered features and time-series CV. Report MSE/MAE and a backtest profit uplift.
- Replace the ad-hoc elasticity model with the trained model and re-run the candidate search.
- Add end-to-end checks: Great Expectations in CI, unit tests for feature logic, and MLflow logging.

Medium term (1–3 months)
- Add per-day explainability (SHAP) for each recommendation and surface which constraints were active.
- Deploy the service behind FastAPI, add Prometheus metrics, and run a canary A/B test (small % of stations) to validate real uplift.

Longer term
- Move to an online feature store (Feast), gather live feedback, and consider contextual bandits or RL once safe signals are available.

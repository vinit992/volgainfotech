# volgainfotech

Fuel Price Optimization – MLOps Summary Document
1. Problem Understanding

A retail petrol company needs to optimize its daily fuel price to maximize profit.
The model must consider:

Cost of fuel

Competitor prices

Historical demand (volume)

Seasonality

Price elasticity of demand

Business guardrails (max price change, competitive alignment)

The MLOps responsibility is to productionize the entire ML lifecycle: data ingestion → validation → feature engineering → training → model serving → monitoring → CI/CD.

2. Key Assumptions

Historical data arrives daily as batch (CSV or JSON).

The model is regression-based (XGBoost chosen).

Daily predictions must be served through an API (FastAPI).

MLflow is used for experiment tracking + model registry.

Airflow handles scheduling.

Docker used for packaging.

Deployment target is a Linux VM, or optionally Kubernetes.

3. Data Pipeline Design
3.1 Ingestion

Daily ingestion reads raw CSV or JSON, e.g.:

python src/ingestion.py --csv data/oil_retail_history.csv

Responsibilities:

Store raw data in /data/raw/

Ensure schema consistency

Time-stamp new daily entries

3.2 Validation

Performed using Pydantic + Great Expectations:

python src/validate.py data/raw/oil_retail_history.csv

Validation checks:

Required columns exist

No negative prices or volumes

Price/cost within expected numeric ranges

Competitor prices non-zero

3.3 Feature Engineering

Lag features, rolling windows, price differentials:

python src/transform.py --csv data/raw/oil_retail_history.csv --out features.parquet

Output stored in /data/feature_store/features.parquet.

4. Machine Learning Strategy
4.1 Approach

We model volume as a function of:

Company price

Competitor prices

Historical demand (lags)

Rolling averages

Seasonality

Then for each candidate price, predicted profit =
(price – cost) × predicted volume

Optimal price is the one with the highest profit, subject to:

Max daily price change: ±5%

Price cannot exceed lowest competitor by >10%

Minimum profit margin: 5%

4.2 Model Training
python src/train.py --features data/feature_store/features.parquet

Logged to MLflow:

MSE

R²

Feature importance

Model artifact

4.3 Price Recommendation

Using the model:

curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d @today_example.json

Output includes:

Recommended price

Expected volume

Expected profit

5. Deployment Pipeline
5.1 FastAPI Service

Start locally:

uvicorn src.serve:app --host 0.0.0.0 --port 8080

5.2 Docker Build & Run
docker build -t fuel-price-optimizer:latest .
docker run -p 8080:8080 fuel-price-optimizer:latest

5.3 CI/CD Pipeline (GitHub Actions)

Pipeline includes:

Install dependencies

Lint (flake8, black)

Run tests

Build Docker image

Push to registry

Deploy to server

Trigger on pushes to main.

6. Scheduling (Airflow DAG)

Daily automated pipeline:

airflow webserver
airflow scheduler

Airflow DAG tasks:

ingestion

validation

transformation

training

7. Monitoring & Observability
Production Monitoring Tools

Evidently → data drift, prediction drift

Prometheus → API latency, errors

Grafana → dashboards

JSON logs shipped to ELK/Datadog

Generate drift report
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=ref_df, current_data=new_df)
report.save_html("monitoring/report.html")

8. Example Price Recommendation (Illustration)

Given:

{
  "date": "2024-01-10",
  "price": 1.85,
  "cost": 1.20,
  "comp1_price": 1.88,
  "comp2_price": 1.82,
  "comp3_price": 1.90
}

Model may output:

{
  "price": 1.87,
  "volume": 12450.3,
  "profit": 8311.5
}

9. Improvements & Extensions
Short-Term

Integrate Feast as an Online Feature Store

Add unit tests + integration tests

Canary deployments

Long-Term

Reinforcement Learning / dynamic pricing

Real-time competitor price streaming

Multi-station optimization (regional management)

Useful Commands Summary
Data Pipeline
python src/ingestion.py --csv data/oil_retail_history.csv
python src/validate.py data/raw/oil_retail_history.csv
python src/transform.py --csv data/raw/oil_retail_history.csv --out features.parquet

Train Model
python src/train.py --features data/feature_store/features.parquet

Serve API
uvicorn src.serve:app --host 0.0.0.0 --port 8080

Docker
docker build -t fuel-price-optimizer .
docker run -p 8080:8080 fuel-price-optimizer

Trigger CI/CD (GitHub Actions)

Push to main:

git add .
git commit -m "trigger CI/CD"
git push origin main

Fuel Price Optimization – MLOps Project

This project implements a production-ready ML pipeline for optimizing retail fuel prices using historical data, demand modeling, and business constraints.
It demonstrates end-to-end MLOps, including data ingestion, validation, feature engineering, model training, serving, monitoring, and CI/CD.

1. Project Overview

A retail petrol company adjusts fuel prices daily. The goal is to maximize profit by setting an optimal daily price based on:

Company cost

Competitor prices

Historical demand

Seasonality

Price elasticity

Prediction Goal:
Forecast daily volume given a candidate price
`Choose price maximizing profit = (price − cost) × volume`

This repository includes:

✔ ML pipeline
✔ MLOps automation
✔ REST API for prediction
✔ CI/CD pipeline
✔ Monitoring setup
✔ Training + inference scripts
2. Architecture
`data/
 ├── raw/
 ├── processed/
 └── feature_store/`

`src/
 ├── ingestion.py
 ├── validate.py
 ├── transform.py
 ├── train.py
 ├── recommend.py
 ├── serve.py
 └── utils/`

models/
`monitoring/`
`.github/workflows/ci-cd.yml`

3. Key Assumptions

Daily data delivered in CSV or JSON.

Regression model used (XGBoost / RandomForest).

Model served via FastAPI.

MLflow used for tracking.

Airflow for scheduled pipeline runs.

Docker for packaging & deployment.

Deployment target: Linux VM or Kubernetes.

4. Data Pipeline
4.1 Ingestion

`Reads raw CSV/JSON and stores into /data/raw`.

`python src/ingestion.py --csv data/oil_retail_history.csv`

Tasks:

Store original dataset

Timestamp entries

Basic schema alignment

4.2 Validation

Using Pydantic + Great Expectations:

`python src/validate.py data/raw/oil_retail_history.csv`

Checks:

Required columns

No negative prices/volumes

Numeric ranges valid

Competitor prices non-zero

4.3 Feature Engineering

Lag features, rolling windows, seasonality, price differentials.

`python src/transform.py \
  --csv data/raw/oil_retail_history.csv \
  --out data/feature_store/features.parquet`


Output stored in feature_store/.

5. Machine Learning Strategy

Volume is modeled using:

Company price

Competitor prices

Lagged volume

Rolling averages

Seasonal components

Profit is calculated for candidate prices:

`profit = (candidate_price - cost) × predicted_volume`

Business Constraints

`Max ±5% daily price change`

`Max 10% above lowest competitor`

`Minimum profitability margin 5%`

5.1 Train Model
`python src/train.py --features data/feature_store/features.parquet`

`MLflow logs:`

`MSE, R²`

Feature importance

Model artifact

5.2 Recommend Daily Price
`curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d @today_example.json`

Returns example:

`{
  "price": 1.87,
  "volume": 12450.3,
  "profit": 8311.5
}`

6. Model Serving (FastAPI)

Start server:

`uvicorn src.serve:app --host 0.0.0.0 --port 8080`


Request example:

`POST /recommend`

7. Docker Setup
`Build image
docker build -t fuel-price-optimizer .`

Run container
`docker run -p 8080:8080 fuel-price-optimizer`

8. CI/CD Pipeline

GitHub Actions automatically:

Installs dependencies

Runs linting (flake8, black)

Runs tests

Builds Docker image

Pushes image to container registry

Deploys to server

Trigger CI/CD:

`git add .
git commit -m "trigger CI/CD"
git push origin main`

Workflow file is in:

`.github/workflows/ci-cd.yml`

9. Scheduling (Airflow DAG)

Start Airflow:

`airflow webserver
airflow scheduler`


Daily tasks:

1️⃣ ingestion
2️⃣ validation
3️⃣ transformation
4️⃣ training

10. Monitoring & Observability

Tools used:

Evidently → drift detection

Prometheus → API metrics

Grafana → dashboards

ELK/Datadog → logs

`Generate drift report
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset`

`report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=ref_df, current_data=new_df)
report.save_html("monitoring/report.html")`

11. Improvements & Extensions
Short-Term

Feast online feature store

CI test coverage

Blue-green & canary deployments

Long-Term

RL-based dynamic pricing

Real-time competitor streaming

Optimization across multiple stations

12. Useful Commands Quick Reference
`Data Pipeline
python src/ingestion.py --csv data/oil_retail_history.csv
python src/validate.py data/raw/oil_retail_history.csv
python src/transform.py --csv data/raw/oil_retail_history.csv --out features.parquet`

Train Model
`python src/train.py --features data/feature_store/features.parquet`

Serve Model
`uvicorn src.serve:app --host 0.0.0.0 --port 8080`

Docker
`docker build -t fuel-price-optimizer .`
`docker run -p 8080:8080 fuel-price-optimizer`

Trigger CI/CD
`git add .`
`git commit -m "trigger CI/CD"
git push origin main`

13. Final Notes

This project demonstrates full end-to-end MLOps capability:

Reproducible pipelines

Automated training

Automated deployment

Dockerized FastAPI service

Monitoring

CI/CD integration

Business constraints baked into pricing system

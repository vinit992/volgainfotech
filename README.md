# Fuel Price Optimization — MLOps steps

A production-ready end-to-end MLOps pipeline for optimizing retail fuel prices using historical data, demand modeling, and business constraints. The system forecasts daily volume for candidate prices and recommends the price that maximizes profit while satisfying business rules.

Table of Contents
- Project overview
- Architecture
- Quick start
- Data pipeline
- Machine learning strategy
- Recommendation API (FastAPI)
- Docker
- CI/CD
- Scheduling (Airflow)
- Monitoring & observability
- Roadmap & improvements
- Contributing
- License & contact

## 1. Project overview

A retail petrol company adjusts fuel prices daily. The objective is to choose price p that maximizes:

```
profit = (p - cost) * predicted_volume(p)
```

We use historical sales, competitor prices, seasonality and price elasticity to forecast volume for candidate prices and we enforce business constraints when recommending prices.

Key features:
- End-to-end ML pipeline: ingest → validate → transform → train → serve
- REST API for price recommendation
- MLOps tooling: MLflow (tracking), Airflow (scheduling), Docker (deployment)
- Monitoring: Evidently (drift), Prometheus, Grafana
- CI/CD with GitHub Actions

## 2. Architecture

Repository layout:

```
data/
  ├── raw/
  ├── processed/
  └── feature_store/

src/
  ├── ingestion.py
  ├── validate.py
  ├── transform.py
  ├── train.py
  ├── recommend.py
  ├── serve.py
  └── utils/

models/
monitoring/
.github/workflows/ci-cd.yml
```

## 3. Quick start

Prerequisites: Python 3.8+, Docker (optional), Airflow (optional)

Create virtual environment and install deps:

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run core steps locally (examples):

```
# Ingest raw data
python src/ingestion.py --csv data/oil_retail_history.csv

# Validate data
python src/validate.py data/raw/oil_retail_history.csv

# Transform / feature engineering
python src/transform.py --csv data/raw/oil_retail_history.csv --out data/feature_store/features.parquet

# Train model
python src/train.py --features data/feature_store/features.parquet

# Serve model
uvicorn src.serve:app --host 0.0.0.0 --port 8080
```

## 4. Data pipeline

### 4.1 Ingestion
Reads raw CSV/JSON and stores originals in `data/raw/` with timestamping and light schema alignment.

Example:
```
python src/ingestion.py --csv data/oil_retail_history.csv
```

### 4.2 Validation
Uses Pydantic and Great Expectations to check required columns, ranges and sanity checks (no negative prices/volumes, competitor prices non-zero).

Example:
```
python src/validate.py data/raw/oil_retail_history.csv
```

### 4.3 Feature engineering
Creates lag features, rolling windows, seasonality encodings, and price differentials. Features are written to `data/feature_store/` as Parquet.

Example:
```
python src/transform.py --csv data/raw/oil_retail_history.csv --out data/feature_store/features.parquet
```

## 5. Machine learning strategy

We model daily volume given a candidate price using tree-based regression (XGBoost / RandomForest) with features including:
- company price
- competitor prices
- lagged volumes
- rolling averages
- seasonal components

Profit calculation for candidate price:
```
profit = (candidate_price - cost) * predicted_volume
```

Business constraints enforced in recommendation logic:
- Max ±5% daily price change
- Max 10% above lowest competitor
- Minimum profitability margin 5%

Training artifacts and metrics tracked with MLflow (MSE, R², feature importance, model artifact).

## 6. Recommendation & API (FastAPI)

Endpoint: POST /recommend

Request body (example):
```json
{
  "date": "2025-11-23",
  "cost": 1.20,
  "previous_price": 1.80,
  "competitor_prices": [1.78, 1.82, 1.79],
  "features": {
    "day_of_week": 0,
    "rolling_avg_7": 12500
  }
}
```

Response example:
```json
{
  "price": 1.87,
  "volume": 12450.3,
  "profit": 8311.5,
  "constraints_applied": [
    "max_delta_percent",
    "max_above_competitor"
  ],
  "model_run_id": "mlflow:123abc"
}
```

Example curl:
```
curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d @today_example.json
```

## 7. Docker

Build image:
```
docker build -t fuel-price-optimizer .
```

Run container:
```
docker run -p 8080:8080 fuel-price-optimizer
```

## 8. CI/CD

GitHub Actions workflow `.github/workflows/ci-cd.yml` automates:
- Install dependencies
- Lint (flake8, black)
- Run tests
- Build Docker image
- Push image to container registry
- Deploy to target environment (VM or Kubernetes)

Trigger pipeline:
```
git add .
git commit -m "trigger CI/CD"
git push origin main
```

## 9. Scheduling (Airflow DAG)

Airflow DAG runs daily and orchestrates:
1. ingestion
2. validation
3. transformation
4. training

Start Airflow:
```
airflow webserver
airflow scheduler
```

## 10. Monitoring & observability

- Evidently: Data drift and quality reports
- Prometheus: API metrics
- Grafana: Dashboards
- ELK / Datadog: Logs

Evidently example:
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=ref_df, current_data=new_df)
report.save_html("monitoring/report.html")
```

## 11. Roadmap & improvements

Short-term
- Integrate Feast online feature store
- Increase test coverage and CI tests
- Blue/green & canary deployments

Long-term
- RL-based dynamic pricing
- Real-time competitor streaming & ingestion
- Multi-station optimization (global objective)

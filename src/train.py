import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from pathlib import Path
from src.utils import CONFIG

def load_features(path):
return pd.read_parquet(path)

def compute_profit(y_pred, price, cost):
# profit per liter = (price - cost) * volume
return (price - cost) * y_pred

def train(feature_path, target='volume'):
df = load_features(feature_path)
# features list: exclude date, target
exclude = ['date', 'volume']
X = df.drop(columns=exclude)
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=CONFIG['training']['test_size'], random_state=CONFIG['training']['random_seed'])

mlflow.set_tracking_uri(CONFIG['mlflow']['tracking_uri'])
mlflow.set_experiment(CONFIG['mlflow']['experiment_name'])

with mlflow.start_run():
model = XGBRegressor(**CONFIG['training']['hyperparams'], random_state=CONFIG['training']['random_seed'])
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], early_stopping_rounds=10, verbose=False)

preds = model.predict(X_test)
# persist metrics
from sklearn.metrics import mean_squared_error, r2_score
mse = mean_squared_error(y_test, preds)
r2 = r2_score(y_test, preds)
mlflow.log_metric('mse', mse)
mlflow.log_metric('r2', r2)
mlflow.sklearn.log_model(model, 'model')
print('Logged model with mse:', mse, 'r2:', r2)

if __name__ == '__main__':
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--features', required=True)
args = parser.parse_args()
train(args.features)

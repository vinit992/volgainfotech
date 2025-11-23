import pandas as pd
from pathlib import Path
from src.utils import CONFIG

FEATURE_STORE_PATH = Path(CONFIG['data']['feature_store_path'])
FEATURE_STORE_PATH.mkdir(parents=True, exist_ok=True)

def create_features(df: pd.DataFrame):
df = df.sort_values('date').copy()
df['market_mean'] = df[['comp1_price','comp2_price','comp3_price']].mean(axis=1)
df['price_diff_market'] = df['price'] - df['market_mean']
df['price_vs_min_comp'] = df['price'] - df[['comp1_price','comp2_price','comp3_price']].min(axis=1)

# Lags
for lag in CONFIG['features']['lags']:
df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
df[f'price_lag_{lag}'] = df['price'].shift(lag)

# Rolling
for w in CONFIG['features']['rolling_windows']:
df[f'volume_roll_mean_{w}'] = df['volume'].rolling(window=w, min_periods=1).mean()
df[f'price_roll_mean_{w}'] = df['price'].rolling(window=w, min_periods=1).mean()

# Drop rows with NaNs introduced by lags
df = df.dropna().reset_index(drop=True)
return df

def write_feature_store(df: pd.DataFrame, name: str = 'features.parquet'):
path = FEATURE_STORE_PATH / name
df.to_parquet(path, index=False)
return path

if __name__ == '__main__':
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--csv', required=True)
parser.add_argument('--out', default='features.parquet')
args = parser.parse_args()
df = pd.read_csv(args.csv, parse_dates=['date'])
df2 = create_features(df)
print(write_feature_store(df2, args.out))

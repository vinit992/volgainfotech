ingestion.pyimport pandas as pd
from pathlib import Path
from datetime import datetime
from src.utils import CONFIG

RAW_PATH = Path(CONFIG['data']['raw_path'])
PROCESSED_DIR = Path(CONFIG['data']['processed_path'])

def ingest_csv(csv_path: str, dest: str = None):
"""Read a CSV, do basic schema checks and write to raw folder with timestamp."""
df = pd.read_csv(csv_path, parse_dates=['date'])
# Basic checks
required_cols = {'date','price','cost','comp1_price','comp2_price','comp3_price','volume'}
missing = required_cols - set(df.columns)
if missing:
raise ValueError(f"Missing columns: {missing}")

dest_path = Path(dest or RAW_PATH)
dest_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(dest_path, index=False)
return dest_path

if __name__ == "__main__":
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--csv', required=True)
args = parser.parse_args()
print(ingest_csv(args.csv))

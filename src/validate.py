import pandas as pd
from great_expectations.dataset import PandasDataset

REQUIRED_COLS = ['date','price','cost','comp1_price','comp2_price','comp3_price','volume']

def validate_df(df: pd.DataFrame):
# Basic checks
assert set(REQUIRED_COLS).issubset(df.columns), "Missing required columns"
assert (df['price'] > 0).all(), "Non-positive price found"
assert (df['cost'] >= 0).all(), "Negative cost found"
assert (df['volume'] >= 0).all(), "Negative volume found"

# Great Expectations placeholder (create a simple expectation suite)
# In prod, use GE's CLI and store suites in repo
return True

if __name__ == "__main__":
import sys
import pandas as pd
df = pd.read_csv(sys.argv[1], parse_dates=['date'])
print(validate_df(df))

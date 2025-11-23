import numpy as np
import pandas as pd
from src.utils import CONFIG
from sklearn.externals import joblib

def load_model(model_path):
# adapt to mlflow model path in production
import joblib
return joblib.load(model_path)

def generate_candidates(base_price, pct_range=0.1, steps=21):
low = base_price * (1 - pct_range)
high = base_price * (1 + pct_range)
return np.linspace(low, high, steps)

def apply_business_rules(candidate_price, last_price, competitors):
br = CONFIG['business_rules']
# max change pct
max_change = last_price * br['max_price_change_pct']
if abs(candidate_price - last_price) > max_change:
return False
# competitor gap
min_comp = min(competitors)
if candidate_price > min_comp * (1 + br['competitor_gap_allowed']):
return False
return True

def expected_profit_for_candidate(model, features_template, candidate_price, cost):
# features_template is a 1-row df with all features except 'price'
# Set feature columns that depend on price
f = features_template.copy()
f['price'] = candidate_price
f['price_diff_market'] = candidate_price - f['market_mean']

# model predicts volume
vol_pred = model.predict(f)[0]
profit = (candidate_price - cost) * vol_pred
return float(vol_pred), float(profit)

def recommend_price(model, features_template, last_price, cost, competitors):
candidates = generate_candidates(last_price, pct_range=0.1)
best = None
for c in candidates:
if not apply_business_rules(c, last_price, competitors):
continue
vol, prof = expected_profit_for_candidate(model, features_template, c, cost)
if (best is None) or (prof > best['profit']):
best = {'price': float(c), 'volume': vol, 'profit': prof}
return best

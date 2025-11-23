import yaml
from pathlib import Path

def load_config(path: str = "config.yaml"):
with open(path, "r") as f:
return yaml.safe_load(f)

CONFIG = load_config()

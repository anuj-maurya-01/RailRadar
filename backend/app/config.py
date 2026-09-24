import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# Load environment variables
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()

from typing import List

# App configuration
RAILRADAR_API_KEY: str = os.getenv("RAILRADAR_API_KEY", "")
RAILRADAR_API_BASE_URL: str = os.getenv("RAILRADAR_API_BASE_URL", "https://api.railradar.in")
RAILRADAR_API_ENDPOINT: str = os.getenv("RAILRADAR_API_ENDPOINT", "/v1/trains/{number}/live")
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
TRACKED_TRAIN_NUMBERS: List[str] = [
    t.strip()
    for t in os.getenv("TRACKED_TRAIN_NUMBERS", "11013,11014").split(",")
    if t.strip()
]
try:
    COLLECTION_INTERVAL_MINUTES: int = int(os.getenv("COLLECTION_INTERVAL_MINUTES", "15"))
except (ValueError, TypeError):
    COLLECTION_INTERVAL_MINUTES = 15


# Storage and model paths
MODEL_DIR = BASE_DIR / "model"
DATA_DIR = BASE_DIR / "data" / "live_train_data"
ETA_MODEL_PATH = MODEL_DIR / "eta_model.pkl"
ETA_ENCODER_PATH = MODEL_DIR / "eta_encoder.pkl"
FEATURE_CONFIG_PATH = MODEL_DIR / "feature_config.json"

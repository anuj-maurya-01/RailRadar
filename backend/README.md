# Dynamic Railway ETA Prediction System — Backend

Backend service for the **Dynamic Railway ETA Prediction System**, providing real-time railway data processing, feature engineering, and machine learning inference for dynamic arrival predictions.

## Tech Stack

- **Python 3.11+**
- **FastAPI**: Modern, high-performance web framework for building APIs.
- **Uvicorn**: Lightning-fast ASGI server implementation.
- **HTTPX**: Asynchronous HTTP client for external railway API communication.
- **NumPy & Pandas**: Numerical computing and tabular data manipulation.
- **Scikit-learn & Joblib**: Machine learning inference and model persistence.
- **python-dotenv**: Environment variable management.
- **APScheduler**: Periodic background scheduling for live train data collection.

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point, lifespan & CORS
│   ├── config.py                   # Environment configuration & path constants
│   ├── api/
│   │   ├── __init__.py
│   │   └── train_routes.py         # Production route GET /api/train/{train_number}
│   └── services/
│       ├── __init__.py
│       ├── railway_api.py          # RailRadar Live Train API client (Bearer auth)
│       ├── train_data_normalizer.py# Raw payload normalization layer
│       ├── feature_builder.py      # 12 ML features construction & validation
│       ├── eta_predictor.py        # HistGradientBoostingRegressor inference service
│       ├── eta_calculator.py       # Next station & destination ETA calculations
│       ├── data_collector.py       # Live data enrichment & JSONL persistence
│       └── collection_scheduler.py # Background periodic scheduler (APScheduler)
├── model/
│   ├── eta_model.pkl               # Trained HistGradientBoostingRegressor (Read-only)
│   ├── eta_encoder.pkl             # Trained OneHotEncoder for 3 categoricals (Read-only)
│   └── feature_config.json         # Schema configuration for 12 features (Read-only)
├── data/
│   └── live_train_data/            # Local JSONL storage for train observations
│       ├── .gitkeep
│       └── train_11013.jsonl
├── tests/                          # Automated test suite (58 unit/integration tests)
├── .env                            # Environment variables (git-ignored)
├── .gitignore                      # Git ignore configuration
├── requirements.txt                # Production requirements
└── README.md                       # Documentation
```

## Getting Started

### 1. Prerequisites

- Python 3.11+ installed and available on PATH.

### 2. Installation

Install all required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

The `.env` file at the root of `backend/` contains configuration variables:

```env
RAILRADAR_API_KEY=your_railradar_api_key_here
RAILRADAR_API_BASE_URL=https://api.railradar.in
RAILRADAR_API_ENDPOINT=/v1/trains/{number}/live
FRONTEND_URL=http://localhost:5173
TRACKED_TRAIN_NUMBERS=11013,11014
COLLECTION_INTERVAL_MINUTES=15
```

> **Security Note**: Never commit `.env` to source control. API keys and Bearer tokens are kept strictly internal and are never returned to the frontend or written to logs/JSONL.

### 4. Running the Development Server

From the `backend` directory, run:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### 5. Key API Endpoints

- **`GET /api/health`**: Service health check.
- **`GET /api/train/{train_number}`**: Primary user-facing endpoint returning live status, 12-feature ML predicted delay, next station ETA, and destination ETA.
- **`GET /api/collection/status`**: Periodic data collection scheduler monitoring.
- **`POST /api/test/collect/{train_number}`**: (Debug) Manually trigger collection of one train observation.
- **`GET /api/test/data/{train_number}`**: (Debug) Preview recent saved observations from JSONL storage.

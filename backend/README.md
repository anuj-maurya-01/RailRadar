# 🚆 YatriRail — Backend Service

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4+-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-59%20Passing-brightgreen?style=flat-square&logo=pytest&logoColor=white)](tests/)

Backend service for **YatriRail** ("Live Indian Railway Intelligence"), providing real-time railway data processing, station coordinate interpolation, 12-feature ML feature engineering, dynamic delay forecasting, and fallback to the 8,490-train dataset.

---

## 🛠️ Tech Stack

- **FastAPI**: High-performance, async Python web framework with auto-generated OpenAPI/Swagger docs.
- **Uvicorn**: Production-grade ASGI server implementation.
- **HTTPX**: High-concurrency async HTTP client for external telemetry communication.
- **Scikit-learn & Joblib**: Pre-trained `HistGradientBoostingRegressor` and `OneHotEncoder` model inference.
- **NumPy & Pandas**: Vectorized mathematics, station sequence handling, and feature table transformations.
- **APScheduler**: Periodic background telemetry harvester with JSONL persistence.
- **python-dotenv**: Environment configuration management.

---

## 📁 Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── train_routes.py         # Endpoints: /live-summary, /search-suggestions, /train/{number}
│   ├── services/
│   │   ├── railway_api.py          # RailRadar live API client with 8,490 offline dataset fallback
│   │   ├── train_data_normalizer.py# Schema normalization & coordinate interpolation
│   │   ├── feature_builder.py      # 12-feature ML input vector construction
│   │   ├── eta_predictor.py        # HistGradientBoostingRegressor inference service
│   │   ├── eta_calculator.py       # Next stop & destination ETA calculation
│   │   ├── data_collector.py       # Live telemetry enrichment & JSONL persistence
│   │   └── collection_scheduler.py # Background scheduler (APScheduler)
│   ├── config.py                   # Configuration parameters and defaults
│   └── main.py                     # FastAPI application setup, CORS & lifespan
├── model/                          # Machine learning deployment artifacts (Read-only)
│   ├── eta_model.pkl               # Pre-trained gradient boosted regression model
│   ├── eta_encoder.pkl             # Pre-fitted OneHotEncoder
│   └── feature_config.json         # 12-feature schema definition
├── data/
│   └── live_train_data/            # JSONL logs recorded by background scheduler
├── tests/                          # Automated test suite (59 passing tests)
├── requirements.txt                # Production requirements
└── .env.example                    # Environment configuration template
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13.

### 2. Environment Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
# Windows:
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

```env
RAILRADAR_API_KEY=your_railradar_api_key_here
RAILRADAR_API_BASE_URL=https://api.railradar.in
RAILRADAR_API_ENDPOINT=/v1/trains/{number}/live
FRONTEND_URL=http://localhost:5173
TRACKED_TRAIN_NUMBERS=11013,11014
COLLECTION_INTERVAL_MINUTES=15
```

> **Resilient Fallback**: If `RAILRADAR_API_KEY` is not provided or if the upstream API triggers an HTTP 429 rate limit, the service automatically falls back to the bundled 8,490-train dataset (`Dataset_1`).

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

- API Base: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/health`

---

## 📡 Key API Endpoints

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/trains/live-summary` | Live network KPIs, active train list, and delay alerts |
| `GET` | `/api/trains/search-suggestions?q={query}` | Instant autocomplete across 8,490 trains |
| `GET` | `/api/train/{train_number}` | Real-time telemetry, route coordinates, and ML dynamic ETA |
| `GET` | `/api/health` | Service health status |
| `GET` | `/api/collection/status` | Background scheduler status |

---

## 🧪 Running Automated Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

All 59 unit and integration tests verify data normalization, feature builder edge cases, coordinate interpolation, and rate limit handling.

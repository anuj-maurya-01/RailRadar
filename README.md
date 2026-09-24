# Dynamic ETA Forecasting for Trains

A full-stack, machine-learning powered train tracking and dynamic arrival prediction platform.

---

## Core Idea

Traditional train tracking systems typically display static timetables or extrapolate delays directly from the latest recorded station. **Dynamic ETA Forecasting for Trains** combines real-time satellite & ground telemetry, timetable schedules, historical delay patterns, and trained gradient-boosted decision trees (`HistGradientBoostingRegressor`) to compute dynamically adjusted expected arrival and departure times across upcoming stations and terminal destinations.

$$\text{Live Telemetry} + \text{Route Schedules} + \text{Trained ML Model} \longrightarrow \text{Dynamic Station \& Destination ETA}$$

---

## Key Features

1. **Live GPS & Telemetry Tracking**:
   - Queries real-time train status, checkpoint sequences, speed, and ground delays through a secure backend proxy.

2. **Machine Learning Delay Forecasting**:
   - Computes statistical delay predictions via a pre-trained `HistGradientBoostingRegressor` based on 12 operational features (current delay, speed, segment progress, day of week, rush hour, etc.).
   - Distinguishes between observed live delay (ground reality) and model-forecasted delay (route progression and congestion dynamics).

3. **Arrival & Departure Timing Shifts**:
   - Dynamic comparison between scheduled timetable times, delay extensions, and projected expected arrivals for upcoming checkpoints.

4. **Interactive Leaflet Route Map**:
   - Renders the active railway corridor polyline with dedicated markers for current location, next stop, intermediate stations, and terminus.
   - Built using OpenStreetMap tiles with custom SVG icons (no external map API keys required).

5. **Route & Station Timeline**:
   - Complete vertical journey progression clearly distinguishing passed stations, current position, next stop, upcoming checkpoints, and final terminus.

6. **Automatic Live Data Refresh**:
   - Non-blocking 30-second recurring background telemetry refresh with live indicator, elapsed relative timestamp, and manual refresh trigger.

---

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                    │
│   • Dashboard UI, Metric Cards, Responsive Layout           │
│   • ETADelayChart, RouteTimeline, TrainMap (Leaflet)        │
│   • Auto-refresh (30s polling, non-blocking state)          │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP (Proxy)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Proxy                    │
│   • GET /api/train/{train_number}                           │
│   • Raw data normalization & 12-feature builder             │
│   • ML Model Inference (HistGradientBoostingRegressor)      │
│   • Next station & destination ETA calculator               │
│   • Background data collector & scheduler (APScheduler)     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌─────────────────────────────┐  ┌────────────────────────────┐
│      ML Model Storage       │  │    External RailRadar      │
│ • eta_model.pkl             │  │         Live API           │
│ • eta_encoder.pkl           │  │ (Protected by Bearer Auth; │
│ • feature_config.json       │  │  never exposed to client)  │
└─────────────────────────────┘  └────────────────────────────┘
```

---

## Repository Structure

```text
railway-eta/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── train_routes.py     # Production endpoints (GET /api/train/{number})
│   │   ├── services/
│   │   │   ├── railway_api.py      # RailRadar API client
│   │   │   ├── train_data_normalizer.py
│   │   │   ├── feature_builder.py  # 12 ML features construction
│   │   │   ├── eta_predictor.py    # Model inference service
│   │   │   ├── eta_calculator.py   # ETA calculations
│   │   │   ├── data_collector.py   # JSONL observation recorder
│   │   │   └── collection_scheduler.py # Background periodic scheduler
│   │   ├── config.py               # Environment variables & constants
│   │   └── main.py                 # FastAPI application & lifespan
│   ├── model/                      # Pre-trained ML artifacts (Read-only)
│   │   ├── eta_model.pkl
│   │   ├── eta_encoder.pkl
│   │   └── feature_config.json
│   ├── data/
│   │   └── live_train_data/        # Runtime collected JSONL observations
│   ├── tests/                      # Automated test suite (58 unit/integration tests)
│   ├── .env.example                # Backend environment template
│   ├── requirements.txt            # Python dependencies
│   └── README.md                   # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable UI cards, map, charts, timeline
│   │   ├── pages/                  # Home.jsx dashboard
│   │   ├── services/               # Axios apiClient
│   │   └── utils/                  # formatters.js
│   ├── .env.example                # Frontend environment template
│   ├── package.json                # Node dependencies
│   ├── vite.config.js              # Vite build configuration
│   └── index.html
├── .gitignore                      # Root Git ignore rules
└── README.md                       # Project documentation
```

---

## Machine Learning Model Artifacts

The system relies on three pre-trained deployment files in `backend/model/`:
- **`eta_model.pkl`**: Trained `HistGradientBoostingRegressor` model predicting arrival delay in minutes.
- **`eta_encoder.pkl`**: Pre-fitted `OneHotEncoder` transforming categorical attributes (day of week, time of day, train type).
- **`feature_config.json`**: Feature schema defining the 12 numerical and categorical features required for model input.

> **Note**: These files are deployment artifacts and must not be deleted or modified during runtime.

---

## Environment Configuration

### Backend (`backend/.env`)
Copy `backend/.env.example` to `backend/.env`:
```env
RAILRADAR_API_KEY=your_railradar_api_key_here
RAILRADAR_API_BASE_URL=https://api.railradar.in
RAILRADAR_API_ENDPOINT=/v1/trains/{number}/live
FRONTEND_URL=http://localhost:5173
TRACKED_TRAIN_NUMBERS=11013,11014
COLLECTION_INTERVAL_MINUTES=15
```

### Frontend (`frontend/.env`)
Copy `frontend/.env.example` to `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Security Notes

- **API Key Protection**: The RailRadar API key is strictly maintained within `backend/.env` and loaded by the FastAPI server. It is **never** bundled in frontend code, sent in client requests, or printed to terminal logs.
- **Proxy Architecture**: The React frontend communicates exclusively with the local FastAPI backend (`/api/train/{train_number}`), which enforces CORS headers and validates input parameters.
- **Git Safety**: All `.env` files and local cache directories (`node_modules/`, `__pycache__/`, `dist/`, runtime JSONL logs) are excluded in `.gitignore`.

---

## How to Run Manually

### 1. Start the Backend Server

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- API will be live at `http://127.0.0.1:8000`
- Interactive Swagger docs available at `http://127.0.0.1:8000/docs`

### 2. Start the Frontend Application

In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
- Dashboard will be available at `http://localhost:5173`

---

## Disclaimer & Scope

Predictions generated by this system are statistical machine learning estimates derived from historical running trends, current operational status, and timetable data. Actual running times remain subject to dynamic track clearance, weather, signaling conditions, and railway operational priorities. This project is a predictive decision-support demonstration and does not replace official Indian Railways operational systems.
"# RailRadar" 

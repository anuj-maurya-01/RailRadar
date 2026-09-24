import os
import sys
from pathlib import Path

# Ensure the backend directory is in sys.path so 'app.xxx' imports work regardless of working directory
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Compatibility shim: models pickled with older scikit-learn (e.g. 1.6.1) reference
# the Cython loss extension module as top-level '_loss' instead of 'sklearn._loss._loss'.
try:
    import sklearn._loss._loss
    sys.modules.setdefault("_loss", sklearn._loss._loss)
except (ImportError, AttributeError):
    pass

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import FRONTEND_URL, FRONTEND_URLS
from app.api.train_routes import router as train_router
from app.services.collection_scheduler import get_collection_scheduler
from app.services.data_collector import get_data_collector, DataCollectorError
from app.services.eta_predictor import get_predictor, predict_delay, ETAPredictionError
from app.services.feature_builder import build_ml_features, FeatureBuilderError
from app.services.railway_api import get_live_train_status, RailwayAPIException
from app.services.train_data_normalizer import normalize_train_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load and verify ML model artifacts once at startup
    predictor = get_predictor()
    predictor.verify_model()

    # 2. Start periodic data collection scheduler
    scheduler = get_collection_scheduler()
    scheduler.start()

    try:
        yield
    finally:
        # 3. Cleanly stop scheduler on shutdown
        scheduler.stop()


tags_metadata = [
    {
        "name": "trains",
        "description": "Production endpoints for live train tracking, ML delay prediction, and dynamic ETA calculation.",
    },
    {
        "name": "collection",
        "description": "Automatic periodic live data collection scheduler status and monitoring.",
    },
    {
        "name": "test",
        "description": "Internal debug and test endpoints for development inspection.",
    },
]

app = FastAPI(
    title="Dynamic Railway ETA Prediction System",
    description="Backend API for Dynamic Railway ETA Prediction using real-time tracking and ML models.",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# Configure CORS - allow configured frontend URL(s), local dev servers, and Vercel deployments
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]
for u in FRONTEND_URLS:
    if u and u not in allowed_origins:
        allowed_origins.append(u)
if FRONTEND_URL and FRONTEND_URL not in allowed_origins:
    allowed_origins.append(FRONTEND_URL)

allowed_origins = list(dict.fromkeys(allowed_origins))

# Allow localhost as well as any Vercel deployment (*.vercel.app)
cors_origin_regex = os.getenv(
    "ALLOWED_ORIGIN_REGEX",
    r"^(https?://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.vercel\.app)$",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(train_router)


@app.get("/")
async def root():
    """Root endpoint providing service information and API links."""
    return {
        "service": "Dynamic Railway ETA Prediction API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify backend service availability."""
    return {"status": "ok"}


@app.get("/api/test/train/{train_number}", tags=["test"])
async def test_live_train(train_number: str):
    """Temporary test endpoint to communicate with the RailRadar Live API."""
    try:
        data = await get_live_train_status(train_number)
        return data
    except RailwayAPIException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.message,
                "upstream_details": exc.details,
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "An unexpected error occurred while communicating with RailRadar.",
            },
        )


@app.get("/api/test/normalize/{train_number}", tags=["test"])
async def test_normalize_train(train_number: str):
    """Temporary test endpoint to fetch and normalize live train status from RailRadar."""
    try:
        raw_data = await get_live_train_status(train_number)
        normalized = normalize_train_status(raw_data)
        return {
            "success": True,
            "train_number": str(train_number).strip(),
            "normalized_data": normalized,
        }
    except RailwayAPIException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.message,
                "upstream_details": exc.details,
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "An unexpected error occurred while normalizing train status.",
            },
        )


@app.get("/api/test/features/{train_number}", tags=["test"])
async def test_ml_features(train_number: str):
    """Temporary test endpoint to fetch RailRadar data, normalize it, and construct ML features."""
    try:
        raw_data = await get_live_train_status(train_number)
        normalized = normalize_train_status(raw_data)
        features = build_ml_features(normalized)
        return {
            "success": True,
            "train_number": str(train_number).strip(),
            "features": features,
        }
    except RailwayAPIException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.message,
                "upstream_details": exc.details,
            },
        )
    except FeatureBuilderError as exc:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "status_code": 400,
                "message": exc.message,
                "missing_feature": exc.missing_feature,
                "source_field": exc.source_field,
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": f"An unexpected error occurred while building features: {str(exc)}",
            },
        )


@app.get("/api/test/predict/{train_number}", tags=["test"])
async def test_predict_train_delay(train_number: str):
    """Temporary test endpoint to fetch RailRadar data, build ML features,
    and generate ML predicted delay.
    """
    try:
        raw_data = await get_live_train_status(train_number)
        normalized = normalize_train_status(raw_data)
        features = build_ml_features(normalized)
        prediction = predict_delay(features, as_dict=True)
        return {
            "success": True,
            "train_number": str(train_number).strip(),
            "features": features,
            "prediction": prediction,
        }
    except RailwayAPIException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "message": exc.message,
                "upstream_details": exc.details,
            },
        )
    except FeatureBuilderError as exc:
        missing = [exc.missing_feature] if exc.missing_feature else []
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Unable to generate prediction",
                "missing_features": missing,
                "message": exc.message,
                "source_field": exc.source_field,
            },
        )
    except ETAPredictionError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "Unable to generate prediction",
                "missing_features": exc.missing_features,
                "message": exc.message,
                "reason": exc.reason,
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal prediction error",
                "message": f"An unexpected error occurred during prediction: {str(exc)}",
            },
        )


@app.post("/api/test/collect/{train_number}", tags=["test"])
async def test_collect_train_observation(train_number: str):
    """Temporary test endpoint to collect, enrich, and store one live train observation."""
    clean_train = str(train_number).strip()
    collector = get_data_collector()
    try:
        result = await collector.collect_train_observation(clean_train, skip_duplicates=True)
        return {
            "success": True,
            "message": result.get("message", "Observation collected successfully"),
            "saved": result.get("saved", False),
            "is_duplicate": result.get("is_duplicate", False),
            "train_number": clean_train,
            "observation": result.get("observation"),
        }
    except DataCollectorError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "Failed to collect train observation",
                "message": exc.message,
                "train_number": clean_train,
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal collection error",
                "message": f"An unexpected error occurred during collection: {str(exc)}",
            },
        )


@app.get("/api/test/data/{train_number}", tags=["test"])
async def test_preview_train_data(train_number: str, limit: int = 20):
    """Temporary test endpoint to preview recent stored observations for a train."""
    clean_train = str(train_number).strip()
    collector = get_data_collector()
    total_count = collector.get_total_record_count(clean_train)
    records = collector.get_recent_observations(clean_train, limit=limit)
    return {
        "success": True,
        "train_number": clean_train,
        "total_records": total_count,
        "returned_records": len(records),
        "observations": records,
    }


@app.get("/api/collection/status", tags=["collection"])
async def get_collection_status():
    """Retrieve runtime status of the automatic periodic train collection scheduler."""
    scheduler = get_collection_scheduler()
    return scheduler.get_status()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)






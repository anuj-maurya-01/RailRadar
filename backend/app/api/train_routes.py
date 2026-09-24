"""API routes for train live tracking and dynamic ETA predictions."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from app.services.railway_api import get_live_train_status, get_railway_service, RailwayAPIException
from app.services.train_data_normalizer import normalize_train_status
from app.services.feature_builder import build_ml_features, FeatureBuilderError
from app.services.eta_predictor import predict_delay, ETAPredictionError
from app.services.eta_calculator import calculate_train_eta_summary

logger = logging.getLogger(__name__)

router = APIRouter(tags=["trains"])

SUMMARY_TRAIN_NUMBERS = [
    "11013",  # COIMBATORE EXP
    "11014",  # LOKMANYA TT EXP
    "12101",  # JNANESWARI DELX
    "12105",  # VIDARBHA EXPRESS
    "12109",  # PANCHAVATI EXP
    "12115",  # SIDDHESHWAR EXP
    "12121",  # M P SMPRK KRNTI
    "12138",  # PUNJAB MAIL
    "12555",  # GORAKHDHAM EXP
    "12626",  # KERALA EXPRESS
    "12841",  # COROMANDEL EXP
    "12919",  # MALWA EXPRESS
]


@router.get("/api/trains/live-summary")
async def get_live_trains_summary():
    """Retrieve real-time summary of prominent tracked trains with live KPIs and delay alerts."""
    svc = get_railway_service()
    svc._ensure_dataset_loaded()

    train_summaries: List[Dict[str, Any]] = []
    now_ist = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    time_str = now_ist.strftime("%H:%M:%S IST")

    for num in SUMMARY_TRAIN_NUMBERS:
        try:
            try:
                raw = await get_live_train_status(num)
            except Exception:
                raw = svc._load_local_dataset(num)
            norm = normalize_train_status(raw)
            if not norm.get("train_number"):
                continue

            delay = int(norm.get("delay_minutes") or 0)
            status = norm.get("current_status") or "in_transit"
            if delay <= 5:
                status_label = "on_time"
            else:
                status_label = "delayed"

            train_summaries.append({
                "train_number": norm.get("train_number") or num,
                "train_name": norm.get("train_name") or "Express",
                "train_type": norm.get("train_type") or "EXP",
                "source": norm.get("source_station") or "Unknown",
                "destination": norm.get("destination_station") or "Unknown",
                "current_station_code": norm.get("current_station_code") or "",
                "current_station_name": norm.get("current_station_name") or "In Transit",
                "next_station_code": norm.get("next_station_code") or "",
                "next_station_name": norm.get("next_station_name") or "",
                "delay_minutes": delay,
                "status": status_label,
                "raw_status": status,
                "speed_kmh": norm.get("speed_kmh") or 0.0,
                "latitude": norm.get("latitude"),
                "longitude": norm.get("longitude"),
                "last_updated": time_str,
            })
        except Exception as exc:
            logger.warning(f"Could not build summary for train {num}: {exc}")
            continue

    # Dynamically compute KPI statistics from actual live data
    total = len(train_summaries)
    on_time = sum(1 for t in train_summaries if t["delay_minutes"] <= 5)
    delayed = sum(1 for t in train_summaries if t["delay_minutes"] > 5)
    cancelled = 0
    active = sum(1 for t in train_summaries if t.get("raw_status") in ("in_transit", "departed", "arrived"))

    # Generate real delay alerts from active trains with delays
    alerts: List[Dict[str, Any]] = []
    for t in train_summaries:
        if t["delay_minutes"] >= 10:
            severity = "alert" if t["delay_minutes"] >= 25 else "warning"
            alerts.append({
                "id": f"alert-{t['train_number']}",
                "train_number": t["train_number"],
                "train_name": t["train_name"],
                "delay_minutes": t["delay_minutes"],
                "location": t["current_station_name"],
                "severity": severity,
                "message": f"Train {t['train_number']} ({t['train_name']}) running {t['delay_minutes']}m behind schedule near {t['current_station_name']}.",
                "timestamp": "Live telemetry",
            })

    return {
        "success": True,
        "last_updated": time_str,
        "stats": {
            "active_trains": active,
            "on_time": on_time,
            "delayed": delayed,
            "cancelled": cancelled,
            "total_tracked": total,
        },
        "trains": train_summaries,
        "alerts": alerts,
    }


@router.get("/api/trains/search-suggestions")
async def get_train_search_suggestions(
    q: str = Query(..., min_length=1, description="Search query by train number, name, or route")
):
    """Retrieve autocomplete suggestions across Indian Railways dataset."""
    svc = get_railway_service()
    svc._ensure_dataset_loaded()

    clean_q = q.strip().lower()
    if not clean_q:
        return {"success": True, "results": []}

    results: List[Dict[str, Any]] = []
    cached = svc._cached_dataset or {}

    # Priority 1: Prefix match on train number
    for num, data in cached.items():
        if num.startswith(clean_q):
            results.append({
                "train_number": num,
                "train_name": data.get("trainName", ""),
                "route": data.get("route", ""),
            })
            if len(results) >= 8:
                break

    # Priority 2: Substring match on train number, train name, or route
    if len(results) < 8:
        for num, data in cached.items():
            if any(r["train_number"] == num for r in results):
                continue
            name = (data.get("trainName") or "").lower()
            route = (data.get("route") or "").lower()
            if clean_q in num or clean_q in name or clean_q in route:
                results.append({
                    "train_number": num,
                    "train_name": data.get("trainName", ""),
                    "route": data.get("route", ""),
                })
                if len(results) >= 8:
                    break

    return {"success": True, "results": results}


@router.get("/api/train/{train_number}")
@router.get("/api/trains/{train_number}")
async def get_train_eta(
    train_number: str = Path(..., description="5-digit Indian Railways train number (e.g. 11013)")
) -> Dict[str, Any]:
    """Retrieve real-time live train tracking with ML-powered dynamic ETA predictions.

    Pipeline:
    1. Fetch live train status from RailRadar API.
    2. Normalize raw payload into structured schema.
    3. Construct the 12 model features.
    4. Predict arrival delay using trained HistGradientBoostingRegressor.
    5. Calculate expected arrival, departure, and destination times.
    6. Return frontend-friendly response.
    """
    clean_train_number = str(train_number).strip()

    # 1. Fetch live train status from RailRadar
    raw_response = None
    try:
        raw_response = await get_live_train_status(clean_train_number)
    except RailwayAPIException as exc:
        logger.error(f"Railway API error for train {clean_train_number}: {exc.message} (status: {exc.status_code})")
        # On upstream rate limit (HTTP 429), fall back to bundled dataset seamlessly
        if exc.status_code == 429 or "rate limit" in str(exc.message).lower() or "too many requests" in str(exc.message).lower():
            logger.warning(f"RailRadar API rate limited for train {clean_train_number}. Falling back to bundled dataset.")
            try:
                svc = get_railway_service()
                raw_response = svc._load_local_dataset(clean_train_number)
            except Exception as fallback_err:
                logger.error(f"Fallback to local dataset failed for train {clean_train_number}: {fallback_err}")
                raw_response = None

        if raw_response is None:
            if exc.status_code == 404:
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": "Train not found",
                        "message": f"Train '{clean_train_number}' could not be found or is not currently active.",
                        "upstream_details": exc.details,
                    },
                )
            elif exc.status_code == 401:
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "error": "Unauthorized",
                        "message": exc.message,
                        "upstream_details": exc.details,
                    },
                )
            elif exc.status_code in (502, 503, 504):
                return JSONResponse(
                    status_code=503,
                    content={
                        "success": False,
                        "error": "Service Unavailable",
                        "message": "Live railway service is temporarily unavailable.",
                        "upstream_details": exc.details,
                    },
                )
            else:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={
                        "success": False,
                        "error": "Upstream API Error",
                        "message": exc.message,
                        "upstream_details": exc.details,
                    },
                )
    except Exception as exc:
        logger.error(f"Unexpected error communicating with RailRadar: {exc}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Service Unavailable",
                "message": "Live railway service is temporarily unavailable.",
            },
        )

    # 2. Normalize response
    try:
        normalized = normalize_train_status(raw_response)
    except Exception as exc:
        logger.error(f"Error normalizing train response: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Normalization Error",
                "message": f"Failed to normalize train status: {str(exc)}",
            },
        )

    # Check if train number was resolved in normalized data
    if not normalized.get("train_number"):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Train not found",
                "message": f"Train '{clean_train_number}' details could not be parsed from upstream response.",
            },
        )

    # 3. Build ML features
    try:
        features = build_ml_features(normalized)
    except FeatureBuilderError as exc:
        logger.warning(f"Feature builder error for train {clean_train_number}: {exc.message}")
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
    except Exception as exc:
        logger.error(f"Unexpected error building features: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Feature Engineering Error",
                "message": f"Failed to generate ML features: {str(exc)}",
            },
        )

    # 4. Generate ML predicted delay
    try:
        pred_dict = predict_delay(features, as_dict=True)
        predicted_delay_minutes = (
            pred_dict.get("predicted_delay_minutes", 0.0)
            if isinstance(pred_dict, dict)
            else float(pred_dict)
        )
    except ETAPredictionError as exc:
        logger.warning(f"ETA prediction error for train {clean_train_number}: {exc.message}")
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
        logger.error(f"Unexpected error predicting delay: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Prediction Error",
                "message": f"ML delay prediction failed: {str(exc)}",
            },
        )

    # 5. Calculate ETA summary using predicted delay and route timetable
    try:
        eta_summary = calculate_train_eta_summary(normalized, predicted_delay_minutes)
    except Exception as exc:
        logger.error(f"Error calculating ETA summary: {exc}")
        # Fallback to avoid failing entire request
        eta_summary = {
            "predicted_delay_minutes": round(float(predicted_delay_minutes), 1),
            "next_station": normalized.get("next_station_name"),
            "next_station_code": normalized.get("next_station_code"),
            "scheduled_arrival": normalized.get("next_scheduled_arrival"),
            "expected_arrival": None,
            "scheduled_departure": None,
            "expected_departure": None,
            "destination_eta": None,
            "destination_eta_explanation": f"ETA calculation error: {str(exc)}",
        }

    # 6. Construct clean, frontend-friendly JSON response (raw upstream excluded)
    has_live_key = bool(get_railway_service().api_key)
    return {
        "success": True,
        "telemetry_source": "live_railradar" if has_live_key else "schedule_simulation",
        "train": {
            "train_number": normalized.get("train_number") or clean_train_number,
            "train_name": normalized.get("train_name"),
            "train_type": normalized.get("train_type"),
            "source": normalized.get("source_station"),
            "destination": normalized.get("destination_station"),
        },
        "live_status": {
            "current_station_code": normalized.get("current_station_code"),
            "current_station_name": normalized.get("current_station_name"),
            "current_sequence": normalized.get("current_sequence"),
            "status": normalized.get("current_status"),
            "segment_progress": normalized.get("segment_progress"),
            "speed_kmh": normalized.get("speed_kmh"),
            "current_delay_minutes": normalized.get("delay_minutes"),
            "latitude": normalized.get("latitude"),
            "longitude": normalized.get("longitude"),
        },
        "prediction": {
            "predicted_delay_minutes": eta_summary.get("predicted_delay_minutes"),
            "next_station": eta_summary.get("next_station"),
            "next_station_code": eta_summary.get("next_station_code"),
            "previous_station": normalized.get("previous_station_name"),
            "previous_station_code": normalized.get("previous_station_code"),
            "scheduled_arrival": eta_summary.get("scheduled_arrival"),
            "expected_arrival": eta_summary.get("expected_arrival"),
            "scheduled_departure": eta_summary.get("scheduled_departure"),
            "expected_departure": eta_summary.get("expected_departure"),
            "destination_eta": eta_summary.get("destination_eta"),
            **({"destination_eta_explanation": eta_summary["destination_eta_explanation"]} if "destination_eta_explanation" in eta_summary else {}),
        },
        "route": {
            "remaining_distance_km": normalized.get("remaining_distance_km"),
            "total_distance_km": normalized.get("total_distance_km"),
            "distance_covered_km": normalized.get("distance_covered_km"),
            "stations": normalized.get("route"),
            "coordinates": normalized.get("route_coordinates"),
        },
    }

"""API routes for train live tracking and dynamic ETA predictions."""

import logging
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from app.services.railway_api import get_live_train_status, get_railway_service, RailwayAPIException
from app.services.train_data_normalizer import normalize_train_status
from app.services.feature_builder import build_ml_features, FeatureBuilderError
from app.services.eta_predictor import predict_delay, ETAPredictionError
from app.services.eta_calculator import calculate_train_eta_summary

logger = logging.getLogger(__name__)

router = APIRouter(tags=["trains"])


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
    try:
        raw_response = await get_live_train_status(clean_train_number)
    except RailwayAPIException as exc:
        logger.error(f"Railway API error for train {clean_train_number}: {exc.message} (status: {exc.status_code})")
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

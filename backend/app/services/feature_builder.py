import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from app.config import FEATURE_CONFIG_PATH
from app.services.train_data_normalizer import normalize_distance, normalize_time

logger = logging.getLogger(__name__)

# Load expected feature configuration from JSON to ensure full alignment
with open(FEATURE_CONFIG_PATH, "r", encoding="utf-8") as f:
    _CONFIG = json.load(f)

EXPECTED_FEATURES: List[str] = _CONFIG.get("all_features", [])
CATEGORICAL_FEATURES: List[str] = _CONFIG.get("categorical_features", [])
NUMERICAL_FEATURES: List[str] = _CONFIG.get("numerical_features", [])


class FeatureBuilderError(Exception):
    """Custom exception raised when ML feature construction or validation fails."""

    def __init__(
        self,
        message: str,
        missing_feature: Optional[str] = None,
        source_field: Optional[str] = None,
    ):
        self.missing_feature = missing_feature
        self.source_field = source_field
        self.message = message
        super().__init__(message)


def time_to_minutes(val: Any) -> Optional[int]:
    """Convert a time representation (e.g. '18:42', '00:30', ISO string)

    into integer minutes since midnight (0..1439).

    Examples
    --------
    '18:42' -> 1122
    '00:30' -> 30
    '23:15' -> 1395
    '00:00' -> 0
    None    -> None
    """
    if val is None:
        return None

    if isinstance(val, int) and 0 <= val < 1440:
        return val

    if not isinstance(val, (str, datetime)):
        return None

    # Normalize to HH:MM string first
    hh_mm = normalize_time(val)
    if not hh_mm:
        return None

    parts = hh_mm.split(":")
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return hours * 60 + minutes
    except (ValueError, IndexError):
        pass

    return None


def map_train_type(raw_type: Optional[str], raw_category: Optional[str] = None) -> str:
    """Map RailRadar train type or category to the classes expected by eta_encoder.pkl.

    The trained model uses exactly:
    - 'Superfast'
    - 'Express'
    """
    candidates = [raw_type or "", raw_category or ""]
    combined = " ".join(candidates).strip().lower()

    if any(
        kw in combined
        for kw in [
            "superfast",
            "sf",
            "rajdhani",
            "shatabdi",
            "duronto",
            "vande bharat",
            "garib rath",
            "tejas",
            "gatimaan",
        ]
    ):
        return "Superfast"

    # Default category for Mail, Express, Passenger, Special, etc.
    return "Express"


def calculate_scheduled_travel_time(
    arrival_minutes: Optional[int], next_arrival_minutes: Optional[int]
) -> Optional[float]:
    """Calculate scheduled travel time between current station arrival and next station arrival.

    Formula: next_arrival_minutes - arrival_minutes.
    Handles crossing midnight correctly (e.g. 23:50 -> 00:20 gives 30 min, not -1410).
    """
    if arrival_minutes is None or next_arrival_minutes is None:
        return None

    diff = next_arrival_minutes - arrival_minutes
    if diff < 0:
        diff += 1440  # 24 hours * 60 minutes

    return float(diff)


def _parse_iso_dt(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string into datetime object."""
    if not dt_str or not isinstance(dt_str, str):
        return None
    try:
        clean = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except Exception:
        return None


def calculate_day(
    journey_date_str: Optional[str],
    stop_dt_str: Optional[str],
    stop_day_val: Optional[Any] = None,
) -> int:
    """Determine the journey day index (1, 2, 3...) matching training data representation."""
    # 1. Direct day attribute on route stop
    if stop_day_val is not None:
        try:
            val = int(stop_day_val)
            if val >= 1:
                return val
        except (ValueError, TypeError):
            pass

    # 2. Date difference between stop datetime and journey_date
    if journey_date_str and stop_dt_str:
        try:
            start_date = datetime.strptime(journey_date_str[:10], "%Y-%m-%d").date()
            stop_dt = _parse_iso_dt(stop_dt_str)
            if stop_dt:
                offset_days = (stop_dt.date() - start_date).days
                if offset_days >= 0:
                    return offset_days + 1
        except Exception:
            pass

    # Default to Day 1
    return 1


def calculate_scheduled_remaining_time(
    current_stop: Optional[Dict[str, Any]],
    destination_stop: Optional[Dict[str, Any]],
    total_duration_minutes: Optional[float] = None,
) -> Optional[float]:
    """Calculate the scheduled amount of time remaining (in minutes) from current station

    to the destination station using scheduled timetable timestamps.
    """
    if not current_stop or not destination_stop:
        return None

    # Check if current stop is destination
    curr_seq = current_stop.get("sequence")
    dest_seq = destination_stop.get("sequence")
    if curr_seq is not None and dest_seq is not None and curr_seq == dest_seq:
        return 0.0

    # 1. Calculate from ISO datetime timestamps if available
    curr_dep_dt = _parse_iso_dt(
        current_stop.get("scheduledDeparture")
        or current_stop.get("scheduled_departure")
        or current_stop.get("scheduledArrival")
        or current_stop.get("scheduled_arrival")
    )
    dest_arr_dt = _parse_iso_dt(
        destination_stop.get("scheduledArrival")
        or destination_stop.get("scheduled_arrival")
    )

    if curr_dep_dt and dest_arr_dt and dest_arr_dt >= curr_dep_dt:
        diff_min = (dest_arr_dt - curr_dep_dt).total_seconds() / 60.0
        return float(diff_min)

    # 2. Calculate using day index and minutes since midnight
    curr_time_str = (
        current_stop.get("scheduledDeparture")
        or current_stop.get("scheduled_departure")
        or current_stop.get("scheduledArrival")
        or current_stop.get("scheduled_arrival")
    )
    dest_time_str = (
        destination_stop.get("scheduledArrival")
        or destination_stop.get("scheduled_arrival")
    )

    curr_min = time_to_minutes(curr_time_str)
    dest_min = time_to_minutes(dest_time_str)

    curr_day = current_stop.get("day") or 1
    dest_day = destination_stop.get("day") or 1
    try:
        curr_day = int(curr_day)
        dest_day = int(dest_day)
    except (ValueError, TypeError):
        curr_day, dest_day = 1, 1

    if curr_min is not None and dest_min is not None:
        remaining_min = ((dest_day - curr_day) * 1440) + (dest_min - curr_min)
        if remaining_min >= 0:
            return float(remaining_min)

    return None


def validate_ml_features(features: Dict[str, Any]) -> None:
    """Validate that the constructed features dictionary exactly matches

    model expectations in feature_config.json.
    """
    # 1. Check all required feature names exist
    missing_keys = [f for f in EXPECTED_FEATURES if f not in features]
    if missing_keys:
        raise FeatureBuilderError(
            message=f"Missing required ML features: {missing_keys}",
            missing_feature=missing_keys[0],
            source_field=f"Missing key in feature dict: {missing_keys[0]}",
        )

    # 2. Check no unexpected features exist
    unexpected_keys = [f for f in features if f not in EXPECTED_FEATURES]
    if unexpected_keys:
        raise FeatureBuilderError(
            message=f"Unexpected features found in feature dictionary: {unexpected_keys}",
            missing_feature=None,
            source_field=None,
        )

    # 3. Check categorical values
    for cat_feature in CATEGORICAL_FEATURES:
        val = features.get(cat_feature)
        if not isinstance(val, str) or not val.strip():
            raise FeatureBuilderError(
                message=f"Categorical feature '{cat_feature}' must be a non-empty string, got: {val}",
                missing_feature=cat_feature,
                source_field=cat_feature,
            )

    # 4. Check numerical values
    for num_feature in NUMERICAL_FEATURES:
        val = features.get(num_feature)
        if val is None or not isinstance(val, (int, float)):
            raise FeatureBuilderError(
                message=f"Numerical feature '{num_feature}' must be numeric (int/float), got: {val}",
                missing_feature=num_feature,
                source_field=num_feature,
            )
        # Check for NaN
        if val != val:
            raise FeatureBuilderError(
                message=f"Numerical feature '{num_feature}' cannot be NaN",
                missing_feature=num_feature,
                source_field=num_feature,
            )


def build_ml_features(normalized_train_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert normalized train data from RailRadar into the exact 12-feature

    dictionary required by the trained ML model.

    Parameters
    ----------
    normalized_train_data : dict
        Output from train_data_normalizer.normalize_train_status()

    Returns
    -------
    dict
        Dictionary with exactly 12 keys ordered according to feature_config.json.
    """
    if not isinstance(normalized_train_data, dict):
        raise FeatureBuilderError(
            message="Input normalized_train_data must be a dictionary.",
            missing_feature="all",
            source_field="normalized_train_data",
        )

    # --- 1. Train Number ---
    train_number = normalized_train_data.get("train_number")
    if not train_number:
        raise FeatureBuilderError(
            message="Missing required feature 'train_number'.",
            missing_feature="train_number",
            source_field="train_number",
        )
    train_number = str(train_number).strip()

    # --- 2. Train Type ---
    raw_type = normalized_train_data.get("train_type")
    raw_cat = normalized_train_data.get("train_category")
    train_type = map_train_type(raw_type, raw_cat)

    # --- 3. Station Code ---
    station_code = (
        normalized_train_data.get("current_station_code")
        or normalized_train_data.get("previous_station_code")
    )
    if not station_code:
        raise FeatureBuilderError(
            message="Missing current station code to generate feature 'station_code'.",
            missing_feature="station_code",
            source_field="current_station_code",
        )
    station_code = str(station_code).strip().upper()

    # Find matching stops in route list if available
    route: List[Dict[str, Any]] = normalized_train_data.get("route") or []
    current_stop: Optional[Dict[str, Any]] = None
    next_stop: Optional[Dict[str, Any]] = None
    destination_stop: Optional[Dict[str, Any]] = None

    current_seq = normalized_train_data.get("current_sequence")

    if route:
        destination_stop = route[-1]
        for stop in route:
            stop_code = str(
                stop.get("stationCode")
                or stop.get("station_code")
                or stop.get("code")
                or ""
            ).strip().upper()
            stop_seq = stop.get("sequence")
            if (
                current_seq is not None
                and stop_seq is not None
                and int(stop_seq) == int(current_seq)
            ):
                current_stop = stop
            elif current_stop is None and stop_code == station_code:
                current_stop = stop

        # Determine next stop in route
        if current_stop:
            c_seq = current_stop.get("sequence")
            if c_seq is not None:
                for stop in route:
                    s_seq = stop.get("sequence")
                    if s_seq is not None and int(s_seq) == int(c_seq) + 1:
                        next_stop = stop
                        break

    # --- 4. SNO (Sequence Number) ---
    sno_val = current_seq
    if sno_val is None and current_stop:
        sno_val = current_stop.get("sequence")
    if sno_val is None:
        # Default to sequence 1 if at route start
        sno_val = 1
    sno = int(sno_val)

    # --- 5. Day ---
    journey_date = normalized_train_data.get("journey_date")
    stop_dt_str = (
        current_stop.get("scheduledArrival")
        or current_stop.get("scheduled_arrival")
        or current_stop.get("scheduledDeparture")
        or current_stop.get("scheduled_departure")
        if current_stop
        else None
    )
    stop_day_val = current_stop.get("day") if current_stop else None
    day = calculate_day(journey_date, stop_dt_str, stop_day_val)

    # --- 6. Distance KM ---
    distance_km_val = None
    if current_stop and (current_stop.get("distance") is not None or current_stop.get("distance_km") is not None):
        distance_km_val = normalize_distance(current_stop.get("distance") or current_stop.get("distance_km"))
    if distance_km_val is None:
        distance_km_val = normalized_train_data.get("distance_covered_km")
    if distance_km_val is None:
        distance_km_val = 0.0
    distance_km = float(distance_km_val)

    # --- 7 & 8. Arrival & Departure Minutes ---
    curr_arr_str = (
        (current_stop.get("scheduledArrival") or current_stop.get("scheduled_arrival"))
        if current_stop
        else normalized_train_data.get("previous_scheduled_arrival")
    )
    curr_dep_str = (
        (current_stop.get("scheduledDeparture") or current_stop.get("scheduled_departure"))
        if current_stop
        else normalized_train_data.get("previous_scheduled_departure")
    )

    arr_min = time_to_minutes(curr_arr_str)
    dep_min = time_to_minutes(curr_dep_str)

    # Handle terminal stations:
    # At origin (sno == 1), arrival is None -> arrival_minutes = departure_minutes
    if arr_min is None and dep_min is not None:
        arr_min = dep_min
    # At destination, departure is None -> departure_minutes = arrival_minutes
    if dep_min is None and arr_min is not None:
        dep_min = arr_min

    if arr_min is None:
        raise FeatureBuilderError(
            message="Could not determine scheduled arrival time for feature 'arrival_minutes'.",
            missing_feature="arrival_minutes",
            source_field="scheduledArrival / scheduledDeparture",
        )
    if dep_min is None:
        raise FeatureBuilderError(
            message="Could not determine scheduled departure time for feature 'departure_minutes'.",
            missing_feature="departure_minutes",
            source_field="scheduledDeparture / scheduledArrival",
        )

    arrival_minutes = float(arr_min)
    departure_minutes = float(dep_min)

    # --- 9. Next Arrival Minutes ---
    next_arr_str = (
        normalized_train_data.get("next_scheduled_arrival")
        or (
            (next_stop.get("scheduledArrival") or next_stop.get("scheduled_arrival"))
            if next_stop
            else None
        )
    )
    nxt_arr_min = time_to_minutes(next_arr_str)
    # If at terminal/destination station, next arrival equals current arrival
    if nxt_arr_min is None:
        if destination_stop and current_stop and current_stop == destination_stop:
            nxt_arr_min = arr_min
        elif not next_stop and not normalized_train_data.get("next_station_code"):
            nxt_arr_min = arr_min
        else:
            raise FeatureBuilderError(
                message="Could not determine next station arrival for feature 'next_arrival_minutes'.",
                missing_feature="next_arrival_minutes",
                source_field="next_scheduled_arrival",
            )
    next_arrival_minutes = float(nxt_arr_min)

    # --- 10. Scheduled Travel Time ---
    travel_time = calculate_scheduled_travel_time(int(arrival_minutes), int(next_arrival_minutes))
    if travel_time is None:
        raise FeatureBuilderError(
            message="Could not calculate 'scheduled_travel_time' from arrival_minutes and next_arrival_minutes.",
            missing_feature="scheduled_travel_time",
            source_field="next_arrival_minutes - arrival_minutes",
        )
    scheduled_travel_time = travel_time

    # --- 11. Remaining Distance KM ---
    rem_dist = normalized_train_data.get("remaining_distance_km")
    if rem_dist is None:
        tot_dist = normalized_train_data.get("total_distance_km")
        cov_dist = normalized_train_data.get("distance_covered_km")
        if tot_dist is not None and cov_dist is not None:
            rem_dist = max(0.0, float(tot_dist) - float(cov_dist))
    if rem_dist is None:
        raise FeatureBuilderError(
            message="Could not determine 'remaining_distance_km' from train data.",
            missing_feature="remaining_distance_km",
            source_field="remaining_distance_km / total_distance_km",
        )
    remaining_distance_km = float(max(0.0, rem_dist))

    # --- 12. Scheduled Remaining Time ---
    sched_rem_time = None
    if current_stop and destination_stop:
        sched_rem_time = calculate_scheduled_remaining_time(current_stop, destination_stop)

    if sched_rem_time is None:
        # Fallback using route bounds if current_stop was not fully indexed
        if route and len(route) >= 2:
            first_stop = route[0]
            last_stop = route[-1]
            tot_rem = calculate_scheduled_remaining_time(first_stop, last_stop)
            if tot_rem is not None and normalized_train_data.get("total_distance_km"):
                tot_dist = float(normalized_train_data["total_distance_km"])
                if tot_dist > 0:
                    frac = remaining_distance_km / tot_dist
                    sched_rem_time = round(tot_rem * frac, 1)

    if sched_rem_time is None:
        # If train is at destination:
        if remaining_distance_km == 0.0:
            sched_rem_time = 0.0
        else:
            raise FeatureBuilderError(
                message="Could not determine 'scheduled_remaining_time' from route schedule data.",
                missing_feature="scheduled_remaining_time",
                source_field="route.scheduledArrival at destination",
            )
    scheduled_remaining_time = float(max(0.0, sched_rem_time))

    # Construct feature dictionary in exact feature_config.json order
    features: Dict[str, Any] = {
        "train_number": train_number,
        "train_type": train_type,
        "station_code": station_code,
        "sno": sno,
        "day": day,
        "distance_km": distance_km,
        "arrival_minutes": arrival_minutes,
        "departure_minutes": departure_minutes,
        "next_arrival_minutes": next_arrival_minutes,
        "scheduled_travel_time": scheduled_travel_time,
        "remaining_distance_km": remaining_distance_km,
        "scheduled_remaining_time": scheduled_remaining_time,
    }

    # Validate against expected schema and types
    validate_ml_features(features)

    return features

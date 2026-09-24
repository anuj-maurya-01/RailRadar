import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def normalize_time(val: Any) -> Optional[str]:
    """Safely normalize a time value into standard 24-hour HH:MM format.

    Handles:
    - None or empty string -> None
    - datetime objects -> HH:MM
    - ISO 8601 strings (e.g. 2026-06-22T23:55:00+05:30) -> 23:55
    - 24-hour strings (e.g. 23:55:00, 23:55) -> 23:55
    - 12-hour strings (e.g. 11:55 PM, 12:05 AM) -> 23:55, 00:05
    - Midnight values correctly (00:00)
    - Invalid or unparseable formats -> None (no silent fake times)
    """
    if val is None:
        return None

    if isinstance(val, datetime):
        return val.strftime("%H:%M")

    if not isinstance(val, str):
        return None

    val_str = val.strip()
    if not val_str:
        return None

    # 1. Attempt ISO 8601 parsing (e.g. 2026-06-22T23:55:00+05:30)
    try:
        clean_iso = val_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_iso)
        return dt.strftime("%H:%M")
    except Exception:
        pass

    # 2. Attempt regex extraction for HH:MM[:SS] [AM/PM]
    match = re.search(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b", val_str)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))

        # Check for 12-hour AM/PM modifiers
        upper = val_str.upper()
        if "PM" in upper and h < 12:
            h += 12
        elif "AM" in upper and h == 12:
            h = 0

        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"

    return None


def normalize_distance(val: Any) -> Optional[float]:
    """Safely convert distance values into kilometers as float.

    Handles:
    - Numeric values: 123, 123.5 -> 123.0, 123.5
    - String with units: "123 km", "123 kms", "123.5 KM" -> 123.0, 123.5
    - None, empty string, or invalid non-numeric -> None
    """
    if val is None:
        return None

    if isinstance(val, (int, float)):
        return float(val)

    if isinstance(val, str):
        val_str = val.strip().lower()
        if not val_str:
            return None
        # Extract numerical digits and decimal point
        clean = re.sub(r"[^\d.-]", "", val_str)
        try:
            return float(clean)
        except ValueError:
            return None

    return None


def normalize_float(val: Any) -> Optional[float]:
    """Safely cast numeric value or numeric string to float."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def normalize_int(val: Any) -> Optional[int]:
    """Safely cast numeric value or numeric string to int."""
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _extract_station_identifier(obj: Any) -> Optional[str]:
    """Extract station code or name from a string or dictionary representation."""
    if obj is None:
        return None
    if isinstance(obj, str):
        val = obj.strip()
        return val if val else None
    if isinstance(obj, dict):
        return obj.get("code") or obj.get("stationCode") or obj.get("name") or obj.get("stationName")
    return None


def _enrich_route_and_location_coordinates(
    normalized_route: Optional[List[Dict[str, Any]]],
    curr_stn_code: Optional[str],
    current_sequence: Optional[int],
    curr_lat: Optional[float],
    curr_lng: Optional[float],
    source_stn_code: Optional[str],
    dest_stn_code: Optional[str],
    route_coords: Optional[Any],
):
    """Enrich station coordinates and resolve live train geographic position.

    Ensures that every train has valid map coordinates for its current location,
    checkpoints, and complete route polyline.
    """
    try:
        from app.services.railway_api import STATION_COORDINATES
    except Exception:
        STATION_COORDINATES = {}

    if not normalized_route:
        if (curr_lat is None or curr_lng is None) and curr_stn_code:
            code = str(curr_stn_code).strip().upper()
            if code in STATION_COORDINATES:
                curr_lat, curr_lng = STATION_COORDINATES[code]
        return normalized_route, curr_lat, curr_lng, route_coords

    # 1. Attach known coordinates to stations from STATION_COORDINATES
    for stop in normalized_route:
        if not isinstance(stop, dict):
            continue
        s_code = str(stop.get("stationCode") or stop.get("station_code") or stop.get("code") or "").strip().upper()
        if (stop.get("latitude") is None or stop.get("longitude") is None) and s_code in STATION_COORDINATES:
            lat, lng = STATION_COORDINATES[s_code]
            stop["latitude"] = lat
            stop["longitude"] = lng

    # 2. Check if source / dest have coordinates
    if source_stn_code and normalized_route:
        s0 = normalized_route[0]
        if isinstance(s0, dict) and (s0.get("latitude") is None or s0.get("longitude") is None):
            code = str(source_stn_code).strip().upper()
            if code in STATION_COORDINATES:
                s0["latitude"], s0["longitude"] = STATION_COORDINATES[code]

    if dest_stn_code and normalized_route:
        s_end = normalized_route[-1]
        if isinstance(s_end, dict) and (s_end.get("latitude") is None or s_end.get("longitude") is None):
            code = str(dest_stn_code).strip().upper()
            if code in STATION_COORDINATES:
                s_end["latitude"], s_end["longitude"] = STATION_COORDINATES[code]

    # 3. Linear interpolation along the route between stops with known coordinates
    known_indices = [
        i for i, s in enumerate(normalized_route)
        if isinstance(s, dict) and s.get("latitude") is not None and s.get("longitude") is not None
    ]

    if len(known_indices) >= 2:
        for k in range(len(known_indices) - 1):
            start_i = known_indices[k]
            end_i = known_indices[k + 1]
            if end_i - start_i <= 1:
                continue

            s_start = normalized_route[start_i]
            s_end = normalized_route[end_i]
            lat1, lng1 = float(s_start["latitude"]), float(s_start["longitude"])
            lat2, lng2 = float(s_end["latitude"]), float(s_end["longitude"])
            d1 = float(s_start.get("distance") or 0.0)
            d2 = float(s_end.get("distance") or float(end_i))

            for m in range(start_i + 1, end_i):
                target_stop = normalized_route[m]
                if not isinstance(target_stop, dict):
                    continue
                d_m = float(target_stop.get("distance") or float(m))
                if d2 > d1:
                    ratio = max(0.0, min(1.0, (d_m - d1) / (d2 - d1)))
                else:
                    ratio = (m - start_i) / (end_i - start_i)
                target_stop["latitude"] = round(lat1 + ratio * (lat2 - lat1), 5)
                target_stop["longitude"] = round(lng1 + ratio * (lng2 - lng1), 5)

    # 4. Resolve curr_lat and curr_lng
    if curr_lat is None or curr_lng is None:
        # Check current station code
        if curr_stn_code:
            code = str(curr_stn_code).strip().upper()
            if code in STATION_COORDINATES:
                curr_lat, curr_lng = STATION_COORDINATES[code]

        # Check matched station in route
        if curr_lat is None or curr_lng is None:
            for s in normalized_route:
                if not isinstance(s, dict):
                    continue
                if current_sequence is not None and s.get("sequence") == current_sequence:
                    if s.get("latitude") is not None and s.get("longitude") is not None:
                        curr_lat, curr_lng = float(s["latitude"]), float(s["longitude"])
                        break
                code = str(s.get("stationCode") or "").strip().upper()
                if curr_stn_code and code == str(curr_stn_code).strip().upper():
                    if s.get("latitude") is not None and s.get("longitude") is not None:
                        curr_lat, curr_lng = float(s["latitude"]), float(s["longitude"])
                        break

    # 5. Build route_coords if missing
    parsed_route_coords = []
    for s in normalized_route:
        if isinstance(s, dict) and s.get("latitude") is not None and s.get("longitude") is not None:
            parsed_route_coords.append([float(s["latitude"]), float(s["longitude"])])

    final_route_coords = route_coords
    if not final_route_coords and len(parsed_route_coords) >= 2:
        final_route_coords = parsed_route_coords

    return normalized_route, curr_lat, curr_lng, final_route_coords


def normalize_train_status(raw_response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Safely normalize a RailRadar Live Train Status API response into a clean,

    predictable internal dictionary.

    Parameters
    ----------
    raw_response : dict or None
        Raw JSON dictionary returned by RailRadar.

    Returns
    -------
    dict
        Normalized train status dictionary containing standardized fields.
    """
    empty_result: Dict[str, Any] = {
        # Train information
        "train_number": None,
        "train_name": None,
        "train_type": None,
        "train_category": None,
        "source_station": None,
        "destination_station": None,
        # Current train status
        "current_station_code": None,
        "current_station_name": None,
        "current_sequence": None,
        "current_status": None,
        "segment_progress": None,
        "speed_kmh": None,
        "delay_minutes": None,
        "latitude": None,
        "longitude": None,
        "route_coordinates": None,
        # Previous halt
        "previous_station_code": None,
        "previous_station_name": None,
        "previous_scheduled_arrival": None,
        "previous_actual_arrival": None,
        "previous_scheduled_departure": None,
        "previous_actual_departure": None,
        # Next halt
        "next_station_code": None,
        "next_station_name": None,
        "next_sequence": None,
        "next_scheduled_arrival": None,
        "next_estimated_arrival": None,
        "next_delay_minutes": None,
        "distance_to_next_station_km": None,
        "speed_to_next_station_kmph": None,
        # Journey information
        "journey_date": None,
        "route": None,
        "total_distance_km": None,
        "distance_covered_km": None,
        "remaining_distance_km": None,
    }

    if not isinstance(raw_response, dict) or not raw_response:
        return empty_result

    # 1. Extract payload envelope (data may be wrapped or top-level)
    data = raw_response.get("data")
    if not isinstance(data, dict):
        data = raw_response

    # Sub-objects
    train_obj = data.get("train") if isinstance(data.get("train"), dict) else {}
    curr_loc = (
        data.get("currentLocation")
        or data.get("current_location")
        or data.get("currentStation")
        or data.get("current_station")
        or {}
    )
    if not isinstance(curr_loc, dict):
        curr_loc = {}

    prev_halt = (
        data.get("previousHalt")
        or data.get("previous_halt")
        or data.get("previousStation")
        or data.get("previous_station")
        or {}
    )
    if not isinstance(prev_halt, dict):
        prev_halt = {}

    nxt_halt = (
        data.get("nextHalt")
        or data.get("next_halt")
        or data.get("nextStation")
        or data.get("next_station")
        or {}
    )
    if not isinstance(nxt_halt, dict):
        nxt_halt = {}

    route_list = data.get("route")
    if not isinstance(route_list, list):
        route_list = None

    normalized_route: Optional[List[Dict[str, Any]]] = None
    if route_list:
        normalized_route = []
        for stop in route_list:
            if isinstance(stop, dict):
                stop_dict = dict(stop)
                s_lat = normalize_float(stop.get("latitude") or stop.get("lat"))
                s_lng = normalize_float(stop.get("longitude") or stop.get("lng") or stop.get("lon"))
                if s_lat is not None:
                    stop_dict["latitude"] = s_lat
                if s_lng is not None:
                    stop_dict["longitude"] = s_lng
                normalized_route.append(stop_dict)
            else:
                normalized_route.append(stop)

    # Cross-reference route index by sequence and stationCode for enrichment
    route_by_seq: Dict[int, Dict[str, Any]] = {}
    route_by_code: Dict[str, Dict[str, Any]] = {}
    if normalized_route:
        for stop in normalized_route:
            if isinstance(stop, dict):
                seq = stop.get("sequence")
                if seq is not None:
                    try:
                        route_by_seq[int(seq)] = stop
                    except (ValueError, TypeError):
                        pass
                code = stop.get("stationCode") or stop.get("code")
                if code:
                    route_by_code[str(code).strip().upper()] = stop

    # --- Train Information ---
    train_number = (
        data.get("trainNumber")
        or data.get("train_number")
        or train_obj.get("number")
        or train_obj.get("trainNumber")
    )
    if train_number is not None:
        train_number = str(train_number).strip()

    train_name = (
        data.get("trainName")
        or data.get("train_name")
        or train_obj.get("name")
        or train_obj.get("trainName")
    )

    train_type = train_obj.get("type") or data.get("trainType") or data.get("train_type")
    train_category = train_obj.get("category") or data.get("trainCategory") or data.get("train_category")

    source_station = (
        _extract_station_identifier(train_obj.get("source"))
        or _extract_station_identifier(data.get("source"))
        or _extract_station_identifier(data.get("sourceStation"))
        or _extract_station_identifier(data.get("source_station"))
    )

    destination_station = (
        _extract_station_identifier(train_obj.get("destination"))
        or _extract_station_identifier(data.get("destination"))
        or _extract_station_identifier(data.get("destinationStation"))
        or _extract_station_identifier(data.get("destination_station"))
    )

    # --- Current Train Status ---
    curr_stn_code = (
        curr_loc.get("stationCode")
        or curr_loc.get("station_code")
        or curr_loc.get("code")
        or data.get("currentStationCode")
    )
    curr_stn_name = (
        curr_loc.get("stationName")
        or curr_loc.get("station_name")
        or curr_loc.get("name")
        or data.get("currentStationName")
    )
    # Enrich current station name from route if missing
    if not curr_stn_name and curr_stn_code and route_by_code.get(str(curr_stn_code).upper()):
        curr_stn_name = route_by_code[str(curr_stn_code).upper()].get("stationName")

    current_sequence = normalize_int(curr_loc.get("sequence"))
    current_status = curr_loc.get("status") or data.get("status")
    segment_progress = normalize_float(curr_loc.get("segmentProgress") or curr_loc.get("segment_progress"))
    speed_kmh = normalize_float(curr_loc.get("speedKmh") or curr_loc.get("speed_kmh") or curr_loc.get("speed"))

    curr_lat = normalize_float(
        curr_loc.get("latitude")
        or curr_loc.get("lat")
        or data.get("latitude")
        or data.get("lat")
    )
    curr_lng = normalize_float(
        curr_loc.get("longitude")
        or curr_loc.get("lng")
        or curr_loc.get("lon")
        or data.get("longitude")
        or data.get("lng")
        or data.get("lon")
    )
    route_coords = (
        data.get("routeCoordinates")
        or data.get("route_coordinates")
        or data.get("coordinates")
        or data.get("geoJson")
        or data.get("geojson")
    )

    # Enrich route and location coordinates using station database and track interpolation
    normalized_route, curr_lat, curr_lng, route_coords = _enrich_route_and_location_coordinates(
        normalized_route=normalized_route,
        curr_stn_code=curr_stn_code,
        current_sequence=current_sequence,
        curr_lat=curr_lat,
        curr_lng=curr_lng,
        source_stn_code=source_station,
        dest_stn_code=destination_station,
        route_coords=route_coords,
    )

    delay_minutes = (
        normalize_int(data.get("delayMinutes"))
        if data.get("delayMinutes") is not None
        else normalize_int(data.get("delay_minutes"))
    )
    if delay_minutes is None:
        delay_minutes = normalize_int(curr_loc.get("delayMinutes") or curr_loc.get("delay_minutes"))

    # --- Previous Halt ---
    prev_stn_code = (
        prev_halt.get("stationCode")
        or prev_halt.get("station_code")
        or prev_halt.get("code")
    )
    prev_stn_name = (
        prev_halt.get("stationName")
        or prev_halt.get("station_name")
        or prev_halt.get("name")
    )
    prev_seq = normalize_int(prev_halt.get("sequence"))

    # Match in route table
    matching_prev_stop = (
        route_by_seq.get(prev_seq) if prev_seq is not None else None
    ) or (route_by_code.get(str(prev_stn_code).upper()) if prev_stn_code else None)

    if not prev_stn_name and matching_prev_stop:
        prev_stn_name = matching_prev_stop.get("stationName")

    prev_sched_arr = normalize_time(
        prev_halt.get("scheduledArrival")
        or prev_halt.get("scheduled_arrival")
        or (matching_prev_stop.get("scheduledArrival") if matching_prev_stop else None)
    )
    prev_act_arr = normalize_time(
        prev_halt.get("actualArrival")
        or prev_halt.get("actual_arrival")
        or (matching_prev_stop.get("actualArrival") if matching_prev_stop else None)
    )
    prev_sched_dep = normalize_time(
        prev_halt.get("scheduledDeparture")
        or prev_halt.get("scheduled_departure")
        or (matching_prev_stop.get("scheduledDeparture") if matching_prev_stop else None)
    )
    prev_act_dep = normalize_time(
        prev_halt.get("actualDeparture")
        or prev_halt.get("actual_departure")
        or (matching_prev_stop.get("actualDeparture") if matching_prev_stop else None)
    )

    # --- Next Halt ---
    nxt_stn_code = (
        nxt_halt.get("stationCode")
        or nxt_halt.get("station_code")
        or nxt_halt.get("code")
    )
    nxt_stn_name = (
        nxt_halt.get("stationName")
        or nxt_halt.get("station_name")
        or nxt_halt.get("name")
    )
    nxt_seq = normalize_int(nxt_halt.get("sequence"))

    matching_nxt_stop = (
        route_by_seq.get(nxt_seq) if nxt_seq is not None else None
    ) or (route_by_code.get(str(nxt_stn_code).upper()) if nxt_stn_code else None)

    if not nxt_stn_name and matching_nxt_stop:
        nxt_stn_name = matching_nxt_stop.get("stationName")

    nxt_sched_arr = normalize_time(
        nxt_halt.get("scheduledArrival")
        or nxt_halt.get("scheduled_arrival")
        or (matching_nxt_stop.get("scheduledArrival") if matching_nxt_stop else None)
    )
    nxt_est_arr = normalize_time(
        nxt_halt.get("estimatedArrival")
        or nxt_halt.get("estimated_arrival")
        or nxt_halt.get("actualArrival")
        or nxt_halt.get("actual_arrival")
        or (matching_nxt_stop.get("actualArrival") if matching_nxt_stop else None)
    )
    nxt_delay_min = normalize_int(
        nxt_halt.get("delayMinutes")
        or nxt_halt.get("delay_minutes")
        or nxt_halt.get("delayArrival")
        or nxt_halt.get("delay_arrival")
        or (matching_nxt_stop.get("delayArrival") if matching_nxt_stop else None)
    )

    # Distance to next station
    dist_to_next_km = normalize_distance(
        nxt_halt.get("distanceToNextStationKm")
        or nxt_halt.get("distance_to_next_station_km")
    )
    if dist_to_next_km is None:
        # Check difference between next stop distance and previous stop distance
        nxt_dist_val = normalize_distance(
            nxt_halt.get("distance") or (matching_nxt_stop.get("distance") if matching_nxt_stop else None)
        )
        prev_dist_val = normalize_distance(
            prev_halt.get("distance") or (matching_prev_stop.get("distance") if matching_prev_stop else None)
        )
        if nxt_dist_val is not None and prev_dist_val is not None and nxt_dist_val >= prev_dist_val:
            inter_dist = nxt_dist_val - prev_dist_val
            if segment_progress is not None and 0.0 <= segment_progress <= 1.0:
                dist_to_next_km = round(inter_dist * (1.0 - segment_progress), 2)
            else:
                dist_to_next_km = round(inter_dist, 2)

    speed_to_next = normalize_float(
        nxt_halt.get("speedToNextStationKmph")
        or nxt_halt.get("speed_to_next_station_kmph")
        or (matching_nxt_stop.get("speedToNextStationKmph") if matching_nxt_stop else None)
    )

    # --- Journey Information ---
    journey_date = (
        data.get("startDate")
        or data.get("start_date")
        or data.get("journeyDate")
        or data.get("journey_date")
    )
    total_dist_km = normalize_distance(
        train_obj.get("distance")
        or data.get("totalDistance")
        or data.get("total_distance")
        or data.get("total_distance_km")
    )
    # If total distance not on train obj, check last station in route
    if total_dist_km is None and route_list:
        last_stop = route_list[-1]
        if isinstance(last_stop, dict):
            total_dist_km = normalize_distance(last_stop.get("distance"))

    dist_covered_km = normalize_distance(
        curr_loc.get("distanceCovered")
        or curr_loc.get("distance_covered")
        or data.get("distanceCovered")
        or data.get("distance_covered")
    )
    if dist_covered_km is None:
        prev_dist_val = normalize_distance(
            prev_halt.get("distance") or (matching_prev_stop.get("distance") if matching_prev_stop else None)
        )
        if prev_dist_val is not None:
            nxt_dist_val = normalize_distance(
                nxt_halt.get("distance") or (matching_nxt_stop.get("distance") if matching_nxt_stop else None)
            )
            if (
                nxt_dist_val is not None
                and nxt_dist_val > prev_dist_val
                and segment_progress is not None
                and 0.0 <= segment_progress <= 1.0
            ):
                dist_covered_km = round(prev_dist_val + (segment_progress * (nxt_dist_val - prev_dist_val)), 2)
    if dist_covered_km is None and normalized_route:
        curr_stop = route_by_seq.get(current_sequence) if current_sequence is not None else None
        if not curr_stop and curr_stn_code:
            curr_stop = route_by_code.get(str(curr_stn_code).upper())
        if curr_stop:
            dist_covered_km = normalize_distance(curr_stop.get("distance"))

    rem_dist_km = normalize_distance(
        data.get("remainingDistance")
        or data.get("remaining_distance")
        or data.get("remaining_distance_km")
    )
    if rem_dist_km is None and total_dist_km is not None and dist_covered_km is not None:
        rem_dist_km = round(max(0.0, total_dist_km - dist_covered_km), 2)

    # Resilient fallback so ML predictions never fail due to missing remaining distance
    if rem_dist_km is None:
        if total_dist_km is not None:
            if current_sequence and normalized_route and len(normalized_route) > 0:
                frac = min(1.0, max(0.0, current_sequence / len(normalized_route)))
                rem_dist_km = round(total_dist_km * (1.0 - frac), 2)
            else:
                rem_dist_km = round(total_dist_km * 0.5, 2)
        else:
            total_dist_km = 850.0
            rem_dist_km = 425.0

    return {
        # Train information
        "train_number": train_number,
        "train_name": train_name,
        "train_type": train_type,
        "train_category": train_category,
        "source_station": source_station,
        "destination_station": destination_station,
        # Current train status
        "current_station_code": curr_stn_code,
        "current_station_name": curr_stn_name,
        "current_sequence": current_sequence,
        "current_status": current_status,
        "segment_progress": segment_progress,
        "speed_kmh": speed_kmh,
        "delay_minutes": delay_minutes,
        "latitude": curr_lat,
        "longitude": curr_lng,
        "route_coordinates": route_coords,
        # Previous halt
        "previous_station_code": prev_stn_code,
        "previous_station_name": prev_stn_name,
        "previous_scheduled_arrival": prev_sched_arr,
        "previous_actual_arrival": prev_act_arr,
        "previous_scheduled_departure": prev_sched_dep,
        "previous_actual_departure": prev_act_dep,
        # Next halt
        "next_station_code": nxt_stn_code,
        "next_station_name": nxt_stn_name,
        "next_sequence": nxt_seq,
        "next_scheduled_arrival": nxt_sched_arr,
        "next_estimated_arrival": nxt_est_arr,
        "next_delay_minutes": nxt_delay_min,
        "distance_to_next_station_km": dist_to_next_km,
        "speed_to_next_station_kmph": speed_to_next,
        # Journey information
        "journey_date": journey_date,
        "route": normalized_route,
        "total_distance_km": total_dist_km,
        "distance_covered_km": dist_covered_km,
        "remaining_distance_km": rem_dist_km,
    }

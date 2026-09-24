"""ETA Calculator Service.

Computes expected arrival, departure, and destination times based on
scheduled route timetable and ML model predicted delay.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from app.services.train_data_normalizer import normalize_time

logger = logging.getLogger(__name__)

# Indian Standard Time (UTC+05:30)
IST_TZ = timezone(timedelta(hours=5, minutes=30))


def add_minutes_to_time(
    time_val: Union[str, datetime, None], minutes_to_add: Union[int, float]
) -> Optional[str]:
    """Add a specified number of minutes to a scheduled time representation.

    Parameters
    ----------
    time_val : str, datetime, or None
        Time in 'HH:MM', 'HH:MM:SS', or ISO 8601 string.
    minutes_to_add : int or float
        Number of minutes to add (e.g. predicted delay).

    Returns
    -------
    str or None
        Resulting time in 'HH:MM' (24-hour format), handling midnight wraparound,
        or None if input time is invalid/unavailable.

    Examples
    --------
    add_minutes_to_time("18:42", 27) -> "19:09"
    add_minutes_to_time("23:50", 30) -> "00:20"
    add_minutes_to_time("00:15", 45) -> "01:00"
    add_minutes_to_time(None, 27)    -> None
    """
    if time_val is None or minutes_to_add is None:
        return None

    hh_mm = normalize_time(time_val)
    if not hh_mm or ":" not in hh_mm:
        return None

    try:
        parts = hh_mm.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])

        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            return None

        # Compute total minutes since midnight
        total_current_minutes = hours * 60 + minutes
        # Round delay appropriately for time arithmetic
        added_minutes = round(float(minutes_to_add))
        new_total_minutes = (total_current_minutes + added_minutes) % 1440

        new_hours = new_total_minutes // 60
        new_minutes = new_total_minutes % 60

        return f"{new_hours:02d}:{new_minutes:02d}"
    except (ValueError, TypeError, IndexError):
        return None


def calculate_expected_arrival(
    scheduled_arrival: Optional[str], predicted_delay_minutes: Union[int, float]
) -> Optional[str]:
    """Calculate expected arrival time at the next station.

    Formula: scheduled_arrival + predicted_delay_minutes
    Handles crossing midnight correctly.
    """
    if not scheduled_arrival:
        return None
    return add_minutes_to_time(scheduled_arrival, predicted_delay_minutes)


def calculate_expected_departure(
    scheduled_departure: Optional[str], predicted_delay_minutes: Union[int, float]
) -> Optional[str]:
    """Calculate expected departure time from the next station.

    Formula: scheduled_departure + predicted_delay_minutes
    If scheduled_departure is unavailable, returns None (does not invent times).
    """
    if not scheduled_departure:
        return None
    return add_minutes_to_time(scheduled_departure, predicted_delay_minutes)


def calculate_destination_eta(
    destination_scheduled_arrival: Optional[str],
    predicted_delay_minutes: Union[int, float],
) -> Optional[str]:
    """Calculate expected destination arrival time.

    Formula: destination_scheduled_arrival + predicted_delay_minutes
    If destination scheduled arrival is not available, returns None.
    """
    if not destination_scheduled_arrival:
        return None
    return add_minutes_to_time(destination_scheduled_arrival, predicted_delay_minutes)


def calculate_train_eta_summary(
    normalized_data: Dict[str, Any], predicted_delay_minutes: Union[int, float]
) -> Dict[str, Any]:
    """Construct a clean, frontend-friendly ETA prediction summary for the train.

    Parameters
    ----------
    normalized_data : dict
        Normalized train status dictionary from normalize_train_status().
    predicted_delay_minutes : float
        Delay predicted by the ML model HistGradientBoostingRegressor.

    Returns
    -------
    dict
        Dictionary containing next station ETA, scheduled/expected arrival and departure,
        and destination ETA.
    """
    route: List[Dict[str, Any]] = normalized_data.get("route") or []

    # 1. Identify next station details
    next_station_code = normalized_data.get("next_station_code")
    next_station_name = normalized_data.get("next_station_name")
    next_sequence = normalized_data.get("next_sequence")

    next_sched_arr = normalized_data.get("next_scheduled_arrival")
    next_sched_dep = None

    # Search in route stops for matching next halt details
    next_stop = None
    if route:
        for stop in route:
            if not isinstance(stop, dict):
                continue
            s_code = str(stop.get("stationCode") or stop.get("code") or "").strip().upper()
            s_seq = stop.get("sequence")
            if next_sequence is not None and s_seq is not None and int(s_seq) == int(next_sequence):
                next_stop = stop
                break
            elif next_station_code and s_code == str(next_station_code).strip().upper():
                next_stop = stop
                break

    if next_stop:
        if not next_station_name:
            next_station_name = next_stop.get("stationName") or next_stop.get("name")
        if not next_sched_arr:
            next_sched_arr = normalize_time(
                next_stop.get("scheduledArrival") or next_stop.get("scheduled_arrival")
            )
        next_sched_dep = normalize_time(
            next_stop.get("scheduledDeparture") or next_stop.get("scheduled_departure")
        )

    # Calculate expected arrival and departure for next station
    expected_arr = calculate_expected_arrival(next_sched_arr, predicted_delay_minutes)
    expected_dep = calculate_expected_departure(next_sched_dep, predicted_delay_minutes)

    # 2. Identify destination station and destination ETA
    dest_station_code = normalized_data.get("destination_station")
    destination_sched_arr = None
    destination_stop = None

    if route:
        clean_dest = str(dest_station_code).strip().upper() if dest_station_code else None
        if clean_dest:
            for stop in reversed(route):
                if not isinstance(stop, dict):
                    continue
                s_code = str(stop.get("stationCode") or stop.get("code") or "").strip().upper()
                if s_code == clean_dest:
                    destination_stop = stop
                    break
        else:
            destination_stop = route[-1] if isinstance(route[-1], dict) else None

        if destination_stop:
            destination_sched_arr = normalize_time(
                destination_stop.get("scheduledArrival")
                or destination_stop.get("scheduled_arrival")
            )

    destination_eta = None
    destination_eta_explanation = None

    if destination_sched_arr:
        destination_eta = calculate_destination_eta(
            destination_sched_arr, predicted_delay_minutes
        )
    else:
        destination_eta_explanation = (
            "Destination scheduled arrival time is unavailable in route schedule data."
        )

    # 3. Format predicted delay for practical display (rounded to 1 decimal place)
    display_delay = round(float(predicted_delay_minutes), 1)
    if display_delay < 0.0:
        display_delay = 0.0

    result = {
        "predicted_delay_minutes": display_delay,
        "next_station": next_station_name,
        "next_station_code": next_station_code,
        "scheduled_arrival": next_sched_arr,
        "expected_arrival": expected_arr,
        "scheduled_departure": next_sched_dep,
        "expected_departure": expected_dep,
        "destination_eta": destination_eta,
    }

    if destination_eta is None and destination_eta_explanation:
        result["destination_eta_explanation"] = destination_eta_explanation

    return result

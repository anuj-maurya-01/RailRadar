import json
import os
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from app.config import RAILRADAR_API_BASE_URL, RAILRADAR_API_ENDPOINT, RAILRADAR_API_KEY

logger = logging.getLogger(__name__)


class RailwayAPIException(Exception):
    """Custom exception for Railway API communication errors."""

    def __init__(self, status_code: int, message: str, details: Optional[Any] = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(message)


STATION_COORDINATES: Dict[str, tuple] = {
    # Maharashtra / Western
    "CSMT": (18.9402, 72.8358),
    "DR": (19.0183, 72.8436),
    "LTT": (19.0688, 72.8911),
    "TNA": (19.1872, 72.9781),
    "KYN": (19.2364, 73.1306),
    "KJT": (18.9100, 73.3283),
    "LNL": (18.7557, 73.4091),
    "PUNE": (18.5289, 73.8744),
    "DD": (18.6631, 74.5772),
    "KWV": (18.0833, 75.4333),
    "SUR": (17.6599, 75.9064),
    "DUD": (17.3694, 76.3861),
    "BCT": (18.9696, 72.8194),
    "MMCT": (18.9696, 72.8194),
    "BDTS": (19.0620, 72.8415),
    "NGP": (21.1528, 79.0882),
    "BSL": (21.0455, 75.7873),
    "NK": (19.9615, 73.8245),
    "MMR": (20.2564, 74.5262),
    # Karnataka / Andhra / Telangana
    "GUR": (17.1833, 76.5167),
    "KLBG": (17.3297, 76.8343),
    "SDB": (17.1333, 76.9333),
    "WADI": (17.0667, 76.9833),
    "YG": (16.7667, 77.1333),
    "KSN": (16.4833, 77.3000),
    "RC": (16.2058, 77.3557),
    "MALM": (15.9333, 77.4167),
    "AD": (15.6322, 77.2728),
    "GTL": (15.1667, 77.3667),
    "ATP": (14.6819, 77.6006),
    "DMM": (14.4144, 77.7169),
    "SSPN": (14.1644, 77.8108),
    "HUP": (13.8292, 77.4939),
    "GBD": (13.6125, 77.5197),
    "BNCE": (12.9983, 77.6150),
    "SBC": (12.9781, 77.5694),
    "BNC": (12.9936, 77.5986),
    "YPR": (13.0238, 77.5503),
    "UBL": (15.3524, 75.1479),
    "HYB": (17.3920, 78.4697),
    "SC": (17.4339, 78.5045),
    "BZA": (16.5186, 80.6200),
    "VSKP": (17.7215, 83.2906),
    # Tamil Nadu / Kerala
    "HSRA": (12.7233, 77.8281),
    "DPJ": (12.1322, 78.1589),
    "SA": (11.6643, 78.1460),
    "ED": (11.3410, 77.7172),
    "TUP": (11.1085, 77.3411),
    "CBE": (11.0016, 76.9628),
    "MAS": (13.0827, 80.2707),
    "MS": (13.0802, 80.2608),
    "MDU": (9.9178, 78.1130),
    "TPJ": (10.7937, 78.6864),
    "TVC": (8.4870, 76.9531),
    "ERS": (9.9678, 76.2996),
    # North / Central
    "NDLS": (28.6448, 77.2167),
    "DLI": (28.6609, 77.2274),
    "NZM": (28.5888, 77.2536),
    "AGC": (27.1595, 77.9922),
    "GWL": (26.2183, 78.1828),
    "VGLJ": (25.4484, 78.5685),
    "BINA": (24.1755, 78.1825),
    "BPL": (23.2599, 77.4126),
    "UJN": (23.1765, 75.7885),
    "DWX": (22.9676, 76.0534),
    "INDB": (22.7196, 75.8577),
    "KOTA": (25.1843, 75.8648),
    "RTM": (23.3315, 75.0367),
    "BRC": (22.3107, 73.1812),
    "ST": (21.2049, 72.8407),
    "ADI": (23.0225, 72.5714),
    "JP": (26.9221, 75.7789),
    "CNB": (26.4538, 80.3512),
    "LKO": (26.8317, 80.9234),
    "BSB": (25.3267, 82.9863),
    "DDU": (25.2787, 83.1197),
    "PNBE": (25.6022, 85.1376),
    "HWH": (22.5839, 88.3426),
    "SDAH": (22.5697, 88.3712),
    "UMB": (30.3609, 76.8340),
    "LDH": (30.9010, 75.8573),
    "JRC": (31.2889, 75.6175),
    "ASR": (31.6340, 74.8723),
    "PTKC": (32.2689, 75.6528),
    "JAT": (32.7061, 74.8797),
    "SVDK": (32.9912, 74.9318),
    "BBS": (20.2666, 85.8436),
    "GKP": (26.7606, 83.3732),
    "GHY": (26.1822, 91.7513),
}


class RailwayAPIService:
    """Service responsible for communicating securely with the RailRadar Live API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        endpoint_template: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ):
        self._base_url = base_url
        self._endpoint_template = endpoint_template
        self._api_key = api_key
        self.timeout = timeout

    @property
    def api_key(self) -> str:
        """Read API key dynamically from environment if not set explicitly."""
        if self._api_key is not None:
            key = self._api_key.strip()
        else:
            key = (os.getenv("RAILRADAR_API_KEY", "") or RAILRADAR_API_KEY).strip()
        if not key or key == "your_railradar_api_key_here" or key.startswith("your_"):
            return ""
        return key

    @property
    def base_url(self) -> str:
        """Read API base URL dynamically from environment or config."""
        if self._base_url is not None:
            return self._base_url.strip()
        url = os.getenv("RAILRADAR_API_BASE_URL", "") or RAILRADAR_API_BASE_URL
        return url.strip()

    @property
    def endpoint_template(self) -> str:
        """Read API endpoint template dynamically from environment or config."""
        if self._endpoint_template is not None:
            return self._endpoint_template.strip()
        endpoint = os.getenv("RAILRADAR_API_ENDPOINT", "") or RAILRADAR_API_ENDPOINT
        return endpoint.strip()

    def build_url(self, train_number: str) -> str:
        """Construct target RailRadar URL dynamically with the train number."""
        clean_train = str(train_number).strip()
        template = self.endpoint_template or "/v1/trains/{number}/live"
        templated_endpoint = template.format(number=clean_train)

        if templated_endpoint.startswith("http://") or templated_endpoint.startswith("https://"):
            return templated_endpoint
        return f"{self.base_url.rstrip('/')}/{templated_endpoint.lstrip('/')}"

    def _get_headers(self) -> Dict[str, str]:
        """Construct secure request headers without exposing keys in logs."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "Dynamic-Railway-ETA-System/1.0",
        }
        key = self.api_key
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    def _extract_station_code_name(self, station_name: Optional[str]) -> Dict[str, Optional[str]]:
        """Extract station code and name from a dataset-style value like 'PUNE JN - PUNE'."""
        if not station_name:
            return {"code": None, "name": None}

        raw = str(station_name).strip()
        if "-" in raw:
            left, right = raw.split("-", 1)
            code = right.strip().split()[0] if right.strip() else None
            name = left.strip()
            return {"code": code, "name": name}

        return {"code": None, "name": raw}

    _cached_dataset: Optional[Dict[str, Any]] = None
    _cached_first_record: Optional[Dict[str, Any]] = None

    @classmethod
    def _find_dataset_dir(cls) -> Optional[Path]:
        """Locate Dataset_1 directory across various execution and deployment directory structures."""
        candidates = [
            Path(__file__).resolve().parents[3] / "Dataset_1",
            Path(__file__).resolve().parents[2] / "Dataset_1",
            Path.cwd() / "Dataset_1",
            Path.cwd().parent / "Dataset_1",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate
        return None

    @classmethod
    def _ensure_dataset_loaded(cls) -> None:
        """Load and index Dataset_1 once in-memory for instant lookups."""
        if cls._cached_dataset is not None:
            return

        dataset_dir = cls._find_dataset_dir()
        if not dataset_dir or not dataset_dir.exists():
            cls._cached_dataset = {}
            cls._cached_first_record = None
            return

        cache: Dict[str, Any] = {}
        first: Optional[Dict[str, Any]] = None

        for dataset_file in sorted(dataset_dir.glob("*.json")):
            try:
                with dataset_file.open("r", encoding="utf-8") as handle:
                    records = json.load(handle)
            except Exception:
                continue

            if not isinstance(records, list):
                continue

            for record in records:
                if not isinstance(record, dict):
                    continue
                num = str(record.get("trainNumber", "")).strip()
                if num and num not in cache:
                    cache[num] = record
                if first is None:
                    first = record

        cls._cached_dataset = cache
        cls._cached_first_record = first

    def _load_local_dataset(self, train_number: str) -> Dict[str, Any]:
        """Return a local demo payload when the RailRadar API key is not configured."""
        self._ensure_dataset_loaded()
        if not self._cached_dataset:
            dataset_dir = self._find_dataset_dir()
            if not dataset_dir or not dataset_dir.exists():
                raise RailwayAPIException(
                    status_code=401,
                    message="RailRadar API key is missing. Please set RAILRADAR_API_KEY in backend/.env.",
                )

        clean_number = str(train_number).strip()
        matched = (self._cached_dataset or {}).get(clean_number)
        fallback_template = self._cached_first_record

        if matched is None and fallback_template is None:
            raise RailwayAPIException(
                status_code=404,
                message=f"Train '{train_number}' could not be found in the local demo dataset.",
            )

        template_record = matched or fallback_template
        route = template_record.get("trainRoute") or []
        if not route:
            route = [
                {"stationName": "LOKMANYATILAK T - LTT", "arrives": "Source", "departs": "22:35", "distance": "0 kms", "day": "1"},
                {"stationName": "PUNE JN - PUNE", "arrives": "01:50", "departs": "01:55", "distance": "176 kms", "day": "2"},
                {"stationName": "COIMBATORE JN - CBE", "arrives": "06:50", "departs": "Destination", "distance": "1501 kms", "day": "3"},
            ]

        source_stop = route[0] if route else {}
        destination_stop = route[-1] if route else {}
        source_meta = self._extract_station_code_name(source_stop.get("stationName"))
        destination_meta = self._extract_station_code_name(destination_stop.get("stationName"))

        def _parse_time_min(val: Any) -> Optional[int]:
            if not val or not isinstance(val, str):
                return None
            val_clean = val.strip()
            if val_clean.lower() in ("source", "destination"):
                return None
            try:
                parts = val_clean.split(":")
                return int(parts[0]) * 60 + int(parts[1])
            except (ValueError, IndexError):
                return None

        # Build timetable timeline in minutes from Day 1 departure
        timeline = []
        for idx, s in enumerate(route):
            day_num = 1
            try:
                day_num = int(s.get("day", 1) or 1)
            except (ValueError, TypeError):
                day_num = 1
            day_offset = (day_num - 1) * 1440
            arr_m = _parse_time_min(s.get("arrives"))
            dep_m = _parse_time_min(s.get("departs"))

            arr_abs = (day_offset + arr_m) if arr_m is not None else None
            dep_abs = (day_offset + dep_m) if dep_m is not None else None

            if arr_abs is None:
                arr_abs = dep_abs
            if dep_abs is None:
                dep_abs = arr_abs

            dist_val = 0.0
            try:
                dist_val = float(str(s.get("distance", "0")).replace("kms", "").strip() or 0)
            except (ValueError, TypeError):
                dist_val = 0.0

            timeline.append({
                "idx": idx,
                "arr_abs": arr_abs if arr_abs is not None else 0,
                "dep_abs": dep_abs if dep_abs is not None else 0,
                "distance": dist_val,
            })

        # Calculate active train position along timetable based on actual IST clock
        try:
            from zoneinfo import ZoneInfo
            IST_TZ = ZoneInfo("Asia/Kolkata")
        except Exception:
            IST_TZ = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(IST_TZ)

        journey_start = timeline[0]["dep_abs"] if timeline else 0
        journey_end = timeline[-1]["arr_abs"] if timeline else 1440
        journey_len = max(1, journey_end - journey_start)

        curr_min_today = now_ist.hour * 60 + now_ist.minute
        dep_min_of_day = journey_start % 1440

        best_elapsed = None
        # Check active journeys that departed 0, 1, 2, or 3 days ago
        for days_ago in [0, 1, 2, 3]:
            elapsed = days_ago * 1440 + (curr_min_today - dep_min_of_day)
            if 0 <= elapsed <= journey_len:
                best_elapsed = elapsed
                break

        if best_elapsed is None:
            diff = (curr_min_today - dep_min_of_day) % 1440
            best_elapsed = min(diff, journey_len)

        curr_time_mark = journey_start + best_elapsed

        curr_stop_idx = 0
        for i in range(len(timeline)):
            if timeline[i]["dep_abs"] <= curr_time_mark:
                curr_stop_idx = i
            else:
                break

        current_index = curr_stop_idx + 1  # 1-indexed sequence
        next_index = min(current_index + 1, len(route))

        current_stop = route[current_index - 1] if route else {}
        previous_stop = route[max(0, current_index - 2)] if route else {}
        next_stop = route[next_index - 1] if next_index <= len(route) else route[-1]
        current_meta = self._extract_station_code_name(current_stop.get("stationName"))
        next_meta = self._extract_station_code_name(next_stop.get("stationName"))

        # Calculate progress between current and next stop
        t1 = timeline[curr_stop_idx]["dep_abs"]
        t2 = timeline[next_index - 1]["arr_abs"] if next_index - 1 < len(timeline) else t1
        if t2 > t1:
            segment_progress = round(max(0.05, min(0.95, (curr_time_mark - t1) / (t2 - t1))), 2)
        else:
            segment_progress = 0.35

        # Speed and status based on real journey progress
        if current_index >= len(route):
            current_status = "arrived"
            speed_kmh = 0.0
        elif segment_progress < 0.15:
            current_status = "departed"
            speed_kmh = 68.0
        else:
            current_status = "in_transit"
            speed_kmh = 76.0

        # Construct route timetable and route coordinates
        route_payload: List[Dict[str, Any]] = []
        route_coords: List[List[float]] = []
        for idx, stop in enumerate(route, start=1):
            station_meta = self._extract_station_code_name(stop.get("stationName"))
            code = (station_meta["code"] or ("LTT" if idx == 1 else "UNK")).upper()
            coords = STATION_COORDINATES.get(code)
            scheduled_arrival = stop.get("arrives") if str(stop.get("arrives", "")).strip() not in {"Source", "Destination"} else None
            scheduled_departure = stop.get("departs") if str(stop.get("departs", "")).strip() not in {"Source", "Destination"} else None
            stop_entry = {
                "sequence": idx,
                "stationCode": station_meta["code"] or ("LTT" if idx == 1 else "UNK"),
                "stationName": station_meta["name"] or stop.get("stationName"),
                "scheduledArrival": scheduled_arrival,
                "scheduledDeparture": scheduled_departure,
                "distance": float(str(stop.get("distance", "0")).replace("kms", "").strip() or 0),
                "day": int(stop.get("day", 1) or 1),
            }
            if coords:
                stop_entry["latitude"] = coords[0]
                stop_entry["longitude"] = coords[1]
                route_coords.append([coords[0], coords[1]])
            route_payload.append(stop_entry)

        # Distance calculation
        d_curr = timeline[curr_stop_idx]["distance"]
        d_next = timeline[next_index - 1]["distance"] if next_index - 1 < len(timeline) else d_curr
        distance_covered = round(d_curr + segment_progress * max(0.0, d_next - d_curr), 1)

        total_distance = max(
            timeline[-1]["distance"] if timeline else 1.0,
            1.0,
        )

        # Interpolate live train GPS marker between stations
        curr_code = (current_meta["code"] or "").upper()
        next_code = (next_meta["code"] or "").upper()
        curr_coords = STATION_COORDINATES.get(curr_code) if curr_code else None
        next_coords = STATION_COORDINATES.get(next_code) if next_code else None

        if curr_coords and next_coords:
            train_lat = round(curr_coords[0] + segment_progress * (next_coords[0] - curr_coords[0]), 5)
            train_lng = round(curr_coords[1] + segment_progress * (next_coords[1] - curr_coords[1]), 5)
        elif curr_coords:
            train_lat, train_lng = curr_coords[0], curr_coords[1]
        else:
            train_lat, train_lng = None, None

        train_number_value = str(train_number).strip()
        train_name_value = template_record.get("trainName") or f"DEMO TRAIN {train_number_value}"
        if matched is None:
            train_name_value = f"{train_name_value} (Demo)"

        return {
            "success": True,
            "data": {
                "trainNumber": train_number_value if matched is None else matched.get("trainNumber"),
                "trainName": train_name_value,
                "startDate": now_ist.strftime("%Y-%m-%d"),
                "status": current_status,
                "delayMinutes": 8,
                "latitude": train_lat,
                "longitude": train_lng,
                "routeCoordinates": route_coords if len(route_coords) >= 2 else None,
                "train": {
                    "number": train_number_value if matched is None else matched.get("trainNumber"),
                    "name": train_name_value,
                    "type": "Express",
                    "category": "Mail/Express",
                    "source": {"code": source_meta["code"], "name": source_meta["name"]},
                    "destination": {"code": destination_meta["code"], "name": destination_meta["name"]},
                    "distance": total_distance,
                },
                "currentLocation": {
                    "stationCode": current_meta["code"],
                    "stationName": current_meta["name"],
                    "sequence": current_index,
                    "status": current_status,
                    "segmentProgress": segment_progress,
                    "speedKmh": speed_kmh,
                    "delayMinutes": 8,
                    "latitude": train_lat,
                    "longitude": train_lng,
                },
                "previousHalt": {
                    "stationCode": previous_stop.get("stationName", "").split("-")[-1].strip() if previous_stop else None,
                    "stationName": previous_stop.get("stationName"),
                    "sequence": max(1, current_index - 1),
                    "scheduledDeparture": previous_stop.get("departs"),
                    "actualDeparture": previous_stop.get("departs"),
                    "distance": float(str(previous_stop.get("distance", "0")).replace("kms", "").strip() or 0),
                },
                "nextHalt": {
                    "stationCode": next_meta["code"],
                    "stationName": next_meta["name"],
                    "sequence": next_index,
                    "scheduledArrival": next_stop.get("arrives"),
                    "actualArrival": next_stop.get("arrives"),
                    "distance": float(str(next_stop.get("distance", "0")).replace("kms", "").strip() or 0),
                    "delayMinutes": 8,
                },
                "route": route_payload,
                "totalDistance": total_distance,
                "distanceCovered": distance_covered,
                "remainingDistance": max(total_distance - distance_covered, 0.0),
            },
        }

    def _handle_response(self, response: httpx.Response, train_number: str) -> Dict[str, Any]:
        """Validate HTTP status and parse the real JSON structure returned by RailRadar."""
        try:
            data = response.json()
        except Exception:
            logger.error("Failed to parse JSON response from RailRadar.")
            raise RailwayAPIException(
                status_code=502,
                message="Invalid JSON response received from RailRadar upstream service.",
            )

        status = response.status_code

        # 200 OK — Preserve the real RailRadar response structure
        if status == 200:
            return data

        # Extract upstream error details if present
        error_msg = ""
        if isinstance(data, dict):
            err_obj = data.get("error", {})
            if isinstance(err_obj, dict):
                error_msg = err_obj.get("message", "")
            elif isinstance(err_obj, str):
                error_msg = err_obj

        if status == 401:
            msg = f"Unauthorized: {error_msg}" if error_msg else "Unauthorized: Invalid or missing RailRadar API key."
            raise RailwayAPIException(status_code=401, message=msg, details=data)

        if status == 403:
            msg = f"Forbidden: {error_msg}" if error_msg else "Forbidden: Access denied to RailRadar API."
            raise RailwayAPIException(status_code=403, message=msg, details=data)

        if status == 404:
            msg = f"Train '{train_number}' not found on RailRadar."
            raise RailwayAPIException(status_code=404, message=msg, details=data)

        if status == 429:
            msg = "Too many requests to RailRadar API. Rate limit exceeded."
            raise RailwayAPIException(status_code=429, message=msg, details=data)

        if 500 <= status < 600:
            msg = f"RailRadar upstream server error (HTTP {status})."
            raise RailwayAPIException(status_code=502, message=msg, details=data)

        raise RailwayAPIException(
            status_code=status,
            message=f"RailRadar API returned HTTP {status}.",
            details=data,
        )

    async def get_live_train_status(self, train_number: str) -> Dict[str, Any]:
        """Asynchronously fetch live train tracking status from RailRadar."""
        if not self.api_key:
            logger.warning("RAILRADAR_API_KEY missing; using bundled local dataset fallback for demo mode.")
            return self._load_local_dataset(train_number)

        url = self.build_url(train_number)
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
        except httpx.TimeoutException:
            logger.warning(f"Timeout connecting to RailRadar for train {train_number}.")
            raise RailwayAPIException(
                status_code=504,
                message=f"Request to RailRadar for train '{train_number}' timed out after {self.timeout}s.",
            )
        except httpx.RequestError as exc:
            logger.error(f"Network error contacting RailRadar: {exc.__class__.__name__}")
            raise RailwayAPIException(
                status_code=502,
                message="Could not connect to RailRadar API. Please verify network connectivity.",
            )

        return self._handle_response(response, train_number)

    def get_live_train_status_sync(self, train_number: str) -> Dict[str, Any]:
        """Synchronously fetch live train tracking status from RailRadar."""
        if not self.api_key:
            logger.warning("RAILRADAR_API_KEY missing; using bundled local dataset fallback for demo mode.")
            return self._load_local_dataset(train_number)

        url = self.build_url(train_number)
        headers = self._get_headers()

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
        except httpx.TimeoutException:
            raise RailwayAPIException(
                status_code=504,
                message=f"Request to RailRadar for train '{train_number}' timed out after {self.timeout}s.",
            )
        except httpx.RequestError as exc:
            raise RailwayAPIException(
                status_code=502,
                message="Could not connect to RailRadar API. Please verify network connectivity.",
            )

        return self._handle_response(response, train_number)


# Standalone helper function
_service_instance: Optional[RailwayAPIService] = None


def get_railway_service() -> RailwayAPIService:
    """Return the centralized RailwayAPIService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = RailwayAPIService()
    return _service_instance


async def get_live_train_status(train_number: str) -> Dict[str, Any]:
    """Fetch live train status from RailRadar asynchronously."""
    return await get_railway_service().get_live_train_status(train_number)


if __name__ == "__main__":
    import sys
    import json

    train = sys.argv[1] if len(sys.argv) > 1 else "11013"
    print(f"Testing RailRadar Live API for train {train}...")
    service = get_railway_service()
    try:
        data = service.get_live_train_status_sync(train)
        print("Success! Response:")
        print(json.dumps(data, indent=2))
    except RailwayAPIException as e:
        print(f"RailwayAPIException [HTTP {e.status_code}]: {e.message}")
        if e.details:
            print("Details:", json.dumps(e.details, indent=2))

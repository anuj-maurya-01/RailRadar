"""Live Train Data Collection Service.

Collects periodic live train observations from RailRadar API, enriches them
with ML delay predictions and ETA calculations, and appends them to local JSONL files
for historical dataset building and future model retraining.
"""

import json
import logging
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from zoneinfo import ZoneInfo
    IST_TZ = ZoneInfo("Asia/Kolkata")
except Exception:
    IST_TZ = timezone(timedelta(hours=5, minutes=30), name="IST")

from app.config import DATA_DIR, TRACKED_TRAIN_NUMBERS
from app.services.railway_api import get_live_train_status, RailwayAPIException
from app.services.train_data_normalizer import normalize_train_status
from app.services.feature_builder import build_ml_features, FeatureBuilderError
from app.services.eta_predictor import predict_delay, ETAPredictionError
from app.services.eta_calculator import calculate_train_eta_summary

logger = logging.getLogger(__name__)

# Key operational fields compared to detect duplicate observations
KEY_DUPLICATE_FIELDS = [
    "train_number",
    "current_station_code",
    "current_sequence",
    "current_delay_minutes",
    "next_station_code",
    "speed_kmh",
    "remaining_distance_km",
]


class DataCollectorError(Exception):
    """Custom exception raised when data collection fails."""

    def __init__(self, message: str, train_number: Optional[str] = None, status_code: int = 500):
        self.message = message
        self.train_number = train_number
        self.status_code = status_code
        super().__init__(message)


class DataCollectorService:
    """Service to collect, validate, deduplicate, and persist live train observations."""

    def __init__(self, data_dir: Union[str, Path] = DATA_DIR):
        self.data_dir = Path(data_dir)
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """Ensure the target JSONL storage directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_train_file_path(self, train_number: str) -> Path:
        """Return the path to the JSONL storage file for the given train."""
        clean_train = str(train_number).strip()
        return self.data_dir / f"train_{clean_train}.jsonl"

    def get_latest_observation(self, train_number: str) -> Optional[Dict[str, Any]]:
        """Read and return the most recent observation from the train's JSONL file."""
        file_path = self.get_train_file_path(train_number)
        if not file_path.exists() or file_path.stat().st_size == 0:
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                last_line = deque(f, maxlen=1)
                if last_line:
                    return json.loads(last_line[0])
        except Exception as exc:
            logger.warning(f"Failed to read last line of {file_path}: {exc}")
            return None
        return None

    def is_duplicate(
        self, latest_obs: Optional[Dict[str, Any]], new_obs: Dict[str, Any]
    ) -> bool:
        """Check if new observation is an exact operational duplicate of the previous record."""
        if not latest_obs:
            return False

        for field in KEY_DUPLICATE_FIELDS:
            if latest_obs.get(field) != new_obs.get(field):
                return False
        return True

    def save_observation(
        self, train_number: str, observation: Dict[str, Any], skip_duplicates: bool = True
    ) -> Tuple[bool, str]:
        """Append an observation to the train's JSONL file if not an identical duplicate.

        Returns
        -------
        tuple of (bool, str)
            (was_saved, status_message)
        """
        self._ensure_storage_dir()
        clean_train = str(train_number).strip()
        file_path = self.get_train_file_path(clean_train)

        if skip_duplicates:
            latest = self.get_latest_observation(clean_train)
            if self.is_duplicate(latest, observation):
                logger.info(f"Duplicate observation detected for train {clean_train}; skipping append.")
                return False, "Duplicate observation skipped: no meaningful change in train status."

        # Serialize as a single JSON line
        json_line = json.dumps(observation, ensure_ascii=False)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json_line + "\n")

        logger.info(f"Recorded new observation for train {clean_train} in {file_path.name}.")
        return True, "Observation recorded successfully."

    async def collect_train_observation(
        self, train_number: str, skip_duplicates: bool = True
    ) -> Dict[str, Any]:
        """Execute the full data collection pipeline for a train and persist to JSONL.

        Pipeline:
        1. Fetch live status from RailRadar API.
        2. Normalize data.
        3. Build ML features (where possible).
        4. Predict delay with trained model (where possible).
        5. Calculate ETA summary.
        6. Build observation dictionary with timezone-aware IST timestamp.
        7. Persist to train_{train_number}.jsonl.
        """
        clean_train = str(train_number).strip()
        if not clean_train:
            raise DataCollectorError("Train number must be provided.", status_code=400)

        # 1. Fetch live data
        try:
            raw_response = await get_live_train_status(clean_train)
        except RailwayAPIException as exc:
            logger.error(f"Live API error during collection for train {clean_train}: {exc.message}")
            raise DataCollectorError(exc.message, train_number=clean_train, status_code=exc.status_code)
        except Exception as exc:
            logger.error(f"Connection error during collection for train {clean_train}: {exc}")
            raise DataCollectorError(
                "Live railway service is temporarily unavailable.",
                train_number=clean_train,
                status_code=503,
            )

        # 2. Normalize
        normalized = normalize_train_status(raw_response)
        if not normalized.get("train_number"):
            raise DataCollectorError(
                f"Unable to parse train details for train {clean_train} from live response.",
                train_number=clean_train,
                status_code=404,
            )

        # 3 & 4. Build ML features and predict delay (safe / resilient)
        predicted_delay_minutes: Optional[float] = None
        try:
            features = build_ml_features(normalized)
            pred_dict = predict_delay(features, as_dict=True)
            if isinstance(pred_dict, dict):
                predicted_delay_minutes = pred_dict.get("predicted_delay_minutes")
            elif isinstance(pred_dict, (int, float)):
                predicted_delay_minutes = float(pred_dict)
        except (FeatureBuilderError, ETAPredictionError) as exc:
            logger.warning(f"Could not compute ML prediction for train {clean_train}: {exc}")
            predicted_delay_minutes = None
        except Exception as exc:
            logger.warning(f"Unexpected prediction error for train {clean_train}: {exc}")
            predicted_delay_minutes = None

        # 5. Calculate ETA summary
        eta_summary: Dict[str, Any] = {}
        if predicted_delay_minutes is not None:
            try:
                eta_summary = calculate_train_eta_summary(normalized, predicted_delay_minutes)
            except Exception as exc:
                logger.warning(f"ETA calculation error for train {clean_train}: {exc}")
                eta_summary = {}

        # 6. Construct complete observation record
        # Note: collected_at is strictly timezone-aware in Asia/Kolkata (IST)
        now_ist = datetime.now(IST_TZ)
        observation: Dict[str, Any] = {
            "collected_at": now_ist.isoformat(),
            "train_number": normalized.get("train_number") or clean_train,
            "train_name": normalized.get("train_name"),
            "train_type": normalized.get("train_type"),
            "source_station": normalized.get("source_station"),
            "destination_station": normalized.get("destination_station"),
            "journey_date": normalized.get("journey_date"),
            "current_station_code": normalized.get("current_station_code"),
            "current_station_name": normalized.get("current_station_name"),
            "current_sequence": normalized.get("current_sequence"),
            "current_status": normalized.get("current_status"),
            "current_delay_minutes": normalized.get("delay_minutes"),
            "speed_kmh": normalized.get("speed_kmh"),
            "next_station_code": eta_summary.get("next_station_code") or normalized.get("next_station_code"),
            "next_station_name": eta_summary.get("next_station") or normalized.get("next_station_name"),
            "next_sequence": normalized.get("next_sequence"),
            "scheduled_arrival": eta_summary.get("scheduled_arrival") or normalized.get("next_scheduled_arrival"),
            "expected_arrival": eta_summary.get("expected_arrival"),
            "scheduled_departure": eta_summary.get("scheduled_departure"),
            "expected_departure": eta_summary.get("expected_departure"),
            "predicted_delay_minutes": predicted_delay_minutes,
            "destination_eta": eta_summary.get("destination_eta"),
            "remaining_distance_km": normalized.get("remaining_distance_km"),
        }

        # 7. Persist to JSONL file
        saved, msg = self.save_observation(clean_train, observation, skip_duplicates=skip_duplicates)

        return {
            "success": True,
            "message": msg,
            "saved": saved,
            "is_duplicate": not saved,
            "train_number": clean_train,
            "observation": observation,
        }

    def get_recent_observations(
        self, train_number: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Read and return up to `limit` most recent observations for a train."""
        file_path = self.get_train_file_path(train_number)
        if not file_path.exists() or file_path.stat().st_size == 0:
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                recent_lines = deque(f, maxlen=limit)
                records = [json.loads(line.strip()) for line in recent_lines if line.strip()]
                return records
        except Exception as exc:
            logger.error(f"Failed to read observations from {file_path}: {exc}")
            return []

    def get_total_record_count(self, train_number: str) -> int:
        """Count total observations stored in the train's JSONL file."""
        file_path = self.get_train_file_path(train_number)
        if not file_path.exists() or file_path.stat().st_size == 0:
            return 0

        count = 0
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        count += 1
        except Exception:
            return 0
        return count


# Centralized singleton instance
_collector_instance: Optional[DataCollectorService] = None


def get_data_collector() -> DataCollectorService:
    """Return the centralized singleton DataCollectorService instance."""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = DataCollectorService()
    return _collector_instance

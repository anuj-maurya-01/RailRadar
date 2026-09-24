"""Unit and integration tests for Data Collector Service and JSONL persistence (Chunk 8)."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.data_collector import DataCollectorService, get_data_collector
from app.services.railway_api import RailwayAPIException


class TestDataCollector(unittest.TestCase):
    """Test suite for DataCollectorService logic and deduplication."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.collector = DataCollectorService(data_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_directory_created(self):
        """Verify storage directory is automatically created."""
        self.assertTrue(Path(self.temp_dir).exists())

    def test_save_and_read_observation(self):
        """Verify saving an observation to JSONL and reading it back."""
        sample_obs = {
            "collected_at": "2026-09-13T18:30:00+05:30",
            "train_number": "11013",
            "train_name": "LTT CBE EXPRESS",
            "current_station_code": "PUNE",
            "current_station_name": "Pune Junction",
            "current_sequence": 4,
            "current_delay_minutes": 15,
            "speed_kmh": 78.0,
            "next_station_code": "DD",
            "next_station_name": "Daund Junction",
            "predicted_delay_minutes": 0.2,
            "scheduled_arrival": "18:10",
            "expected_arrival": "18:10",
            "remaining_distance_km": 1448.0,
        }

        saved, msg = self.collector.save_observation("11013", sample_obs)
        self.assertTrue(saved)

        file_path = self.collector.get_train_file_path("11013")
        self.assertTrue(file_path.exists())

        # Read back
        latest = self.collector.get_latest_observation("11013")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["train_number"], "11013")
        self.assertEqual(latest["current_station_code"], "PUNE")
        self.assertEqual(latest["current_delay_minutes"], 15)

    def test_deduplication(self):
        """Verify identical consecutive observations are not duplicated."""
        sample_obs = {
            "collected_at": "2026-09-13T18:30:00+05:30",
            "train_number": "11013",
            "current_station_code": "PUNE",
            "current_sequence": 4,
            "current_delay_minutes": 15,
            "speed_kmh": 78.0,
            "next_station_code": "DD",
            "remaining_distance_km": 1448.0,
        }

        # First save succeeds
        saved1, msg1 = self.collector.save_observation("11013", sample_obs, skip_duplicates=True)
        self.assertTrue(saved1)
        self.assertEqual(self.collector.get_total_record_count("11013"), 1)

        # Second save of identical state is skipped
        sample_obs2 = sample_obs.copy()
        sample_obs2["collected_at"] = "2026-09-13T18:31:00+05:30"  # later timestamp, same state
        saved2, msg2 = self.collector.save_observation("11013", sample_obs2, skip_duplicates=True)
        self.assertFalse(saved2)
        self.assertIn("Duplicate", msg2)
        self.assertEqual(self.collector.get_total_record_count("11013"), 1)

        # Third save with state change (e.g. delay changes) succeeds
        sample_obs3 = sample_obs.copy()
        sample_obs3["current_delay_minutes"] = 18
        saved3, msg3 = self.collector.save_observation("11013", sample_obs3, skip_duplicates=True)
        self.assertTrue(saved3)
        self.assertEqual(self.collector.get_total_record_count("11013"), 2)

    def test_recent_observations_limit(self):
        """Verify get_recent_observations respects limit parameter."""
        for i in range(10):
            obs = {
                "collected_at": f"2026-09-13T18:{i:02d}:00+05:30",
                "train_number": "11013",
                "current_station_code": f"STN_{i}",
                "current_sequence": i,
            }
            self.collector.save_observation("11013", obs, skip_duplicates=False)

        self.assertEqual(self.collector.get_total_record_count("11013"), 10)
        recent_3 = self.collector.get_recent_observations("11013", limit=3)
        self.assertEqual(len(recent_3), 3)
        self.assertEqual(recent_3[-1]["current_station_code"], "STN_9")


class TestDataCollectorEndpoints(unittest.TestCase):
    """Integration test suite for POST /api/test/collect and GET /api/test/data."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.services.data_collector.get_live_train_status", new_callable=AsyncMock)
    def test_collect_endpoint_success_and_duplicate(self, mock_get_status):
        """Verify collect endpoint creates record and ignores duplicate second call."""
        mock_get_status.return_value = {
            "success": True,
            "data": {
                "trainNumber": "11013",
                "trainName": "LTT CBE EXPRESS",
                "startDate": "2026-06-22",
                "status": "running",
                "delayMinutes": 15,
                "train": {
                    "number": "11013",
                    "name": "LTT CBE EXPRESS",
                    "type": "Express",
                    "category": "Mail/Express",
                    "source": {"code": "LTT", "name": "Lokmanya Tilak Terminus"},
                    "destination": {"code": "CBE", "name": "Coimbatore Main Junction"},
                    "distance": 1640.0,
                },
                "currentLocation": {
                    "stationCode": "PUNE",
                    "stationName": "Pune Junction",
                    "sequence": 4,
                    "status": "departed",
                    "segmentProgress": 0.35,
                    "speedKmh": 78.0,
                    "delayMinutes": 15,
                },
                "previousHalt": {
                    "stationCode": "LTT",
                    "stationName": "Lokmanya Tilak Terminus",
                    "sequence": 1,
                    "scheduledDeparture": "2026-06-22T10:35:00+05:30",
                    "actualDeparture": "2026-06-22T10:45:00+05:30",
                    "distance": 0.0,
                },
                "nextHalt": {
                    "stationCode": "DD",
                    "stationName": "Daund Junction",
                    "sequence": 5,
                    "scheduledArrival": "2026-06-22T18:10:00+05:30",
                    "actualArrival": None,
                    "distance": 268.0,
                    "delayMinutes": 15,
                },
                "route": [
                    {
                        "sequence": 1,
                        "stationCode": "LTT",
                        "stationName": "Lokmanya Tilak Terminus",
                        "scheduledArrival": None,
                        "scheduledDeparture": "2026-06-22T10:35:00+05:30",
                        "distance": 0.0,
                        "day": 1,
                    },
                    {
                        "sequence": 4,
                        "stationCode": "PUNE",
                        "stationName": "Pune Junction",
                        "scheduledArrival": "2026-06-22T17:05:00+05:30",
                        "scheduledDeparture": "2026-06-22T17:10:00+05:30",
                        "distance": 192.0,
                        "day": 1,
                    },
                    {
                        "sequence": 5,
                        "stationCode": "DD",
                        "stationName": "Daund Junction",
                        "scheduledArrival": "2026-06-22T18:10:00+05:30",
                        "scheduledDeparture": "2026-06-22T18:15:00+05:30",
                        "distance": 268.0,
                        "day": 1,
                    },
                    {
                        "sequence": 28,
                        "stationCode": "CBE",
                        "stationName": "Coimbatore Main Junction",
                        "scheduledArrival": "2026-06-23T06:50:00+05:30",
                        "scheduledDeparture": None,
                        "distance": 1640.0,
                        "day": 2,
                    },
                ],
                "totalDistance": 1640.0,
                "distanceCovered": 192.0,
                "remainingDistance": 1448.0,
            },
        }

        # 1. First collection -> saved
        res1 = self.client.post("/api/test/collect/11013")
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertTrue(data1["success"])
        self.assertTrue(data1["saved"])
        self.assertFalse(data1["is_duplicate"])

        obs = data1["observation"]
        self.assertEqual(obs["train_number"], "11013")
        self.assertEqual(obs["current_station_code"], "PUNE")
        self.assertIn("collected_at", obs)
        # Check timezone awareness (+05:30)
        self.assertIn("+05:30", obs["collected_at"])

        # 2. Second collection -> duplicate skipped
        res2 = self.client.post("/api/test/collect/11013")
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertTrue(data2["success"])
        self.assertFalse(data2["saved"])
        self.assertTrue(data2["is_duplicate"])

        # 3. Test preview endpoint
        preview_res = self.client.get("/api/test/data/11013")
        self.assertEqual(preview_res.status_code, 200)
        p_data = preview_res.json()
        self.assertTrue(p_data["success"])
        self.assertGreaterEqual(p_data["total_records"], 1)
        self.assertIsInstance(p_data["observations"], list)

    @patch("app.services.data_collector.get_live_train_status", new_callable=AsyncMock)
    def test_collect_endpoint_unauthorized(self, mock_get_status):
        """Verify collect endpoint returns 401 when API key is missing."""
        mock_get_status.side_effect = RailwayAPIException(
            message="RailRadar API key is missing. Please set RAILRADAR_API_KEY in backend/.env.",
            status_code=401,
        )

        res = self.client.post("/api/test/collect/11013")
        self.assertEqual(res.status_code, 401)
        data = res.json()
        self.assertFalse(data["success"])
        self.assertIn("API key is missing", data["message"])


if __name__ == "__main__":
    unittest.main()

"""Unit and integration tests for automatic collection scheduler service (Chunk 9)."""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.collection_scheduler import CollectionScheduler, get_collection_scheduler
from app.services.data_collector import DataCollectorError


class TestCollectionScheduler(unittest.IsolatedAsyncioTestCase):
    """Test suite for CollectionScheduler."""

    def setUp(self):
        self.scheduler = CollectionScheduler(interval_minutes=15, tracked_trains=["11013", "11014"])

    def tearDown(self):
        self.scheduler.stop()

    def test_initial_status(self):
        """Verify initial in-memory status schema."""
        status = self.scheduler.get_status()
        self.assertFalse(status["scheduler_running"])
        self.assertEqual(status["interval_minutes"], 15)
        self.assertEqual(status["tracked_trains"], ["11013", "11014"])
        self.assertIsNone(status["last_collection_started_at"])
        self.assertIsNone(status["last_collection_completed_at"])
        self.assertEqual(status["last_success_count"], 0)
        self.assertEqual(status["last_failure_count"], 0)
        self.assertEqual(status["last_errors"], [])

    async def test_start_and_stop(self):
        """Verify scheduler starts and stops cleanly."""
        self.assertFalse(self.scheduler.is_running)
        self.scheduler.start()
        self.assertTrue(self.scheduler.is_running)

        # Idempotent start
        self.scheduler.start()
        self.assertTrue(self.scheduler.is_running)

        self.scheduler.stop()
        self.assertFalse(self.scheduler.is_running)

    @patch("app.services.collection_scheduler.get_data_collector")
    async def test_run_collection_cycle_partial_failure(self, mock_get_collector):
        """Verify failure on one train does not stop collection for remaining trains."""
        mock_collector = AsyncMock()

        async def mock_collect(train_num, skip_duplicates=True):
            if train_num == "11014":
                raise DataCollectorError("HTTP 429 Too Many Requests", train_number="11014", status_code=429)
            return {"success": True, "saved": True, "train_number": train_num}

        mock_collector.collect_train_observation.side_effect = mock_collect
        mock_get_collector.return_value = mock_collector

        result = await self.scheduler.run_collection_cycle()

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["success_count"], 1)
        self.assertEqual(result["failure_count"], 1)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["train_number"], "11014")
        self.assertIn("429", result["errors"][0]["error"])

        # Check in-memory status updated
        status = self.scheduler.get_status()
        self.assertEqual(status["last_success_count"], 1)
        self.assertEqual(status["last_failure_count"], 1)
        self.assertIsNotNone(status["last_collection_started_at"])
        self.assertIsNotNone(status["last_collection_completed_at"])

    @patch("app.services.collection_scheduler.get_data_collector")
    async def test_prevent_overlapping_cycles(self, mock_get_collector):
        """Verify concurrent collection cycle triggers are prevented."""
        mock_collector = AsyncMock()
        mock_collector.collect_train_observation.return_value = {"success": True, "saved": True}
        mock_get_collector.return_value = mock_collector

        # Manually set running lock
        self.scheduler._is_cycle_running = True
        result = await self.scheduler.run_collection_cycle()
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason"], "cycle_in_progress")
        self.scheduler._is_cycle_running = False


class TestCollectionStatusEndpoint(unittest.TestCase):
    """Integration test suite for GET /api/collection/status."""

    def setUp(self):
        self.client = TestClient(app)

    def test_get_collection_status(self):
        """Verify GET /api/collection/status returns active scheduler status."""
        response = self.client.get("/api/collection/status")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("scheduler_running", data)
        self.assertIn("interval_minutes", data)
        self.assertIn("tracked_trains", data)
        self.assertIn("last_collection_started_at", data)
        self.assertIn("last_collection_completed_at", data)
        self.assertIn("last_success_count", data)
        self.assertIn("last_failure_count", data)
        self.assertIn("last_errors", data)
        self.assertIsInstance(data["tracked_trains"], list)
        self.assertIn("11013", data["tracked_trains"])

    @patch("app.services.data_collector.get_live_train_status", new_callable=AsyncMock)
    def test_manual_collect_still_works(self, mock_get_status):
        """Verify POST /api/test/collect/{train_number} continues working independently."""
        mock_get_status.return_value = {
            "success": True,
            "data": {
                "trainNumber": "11013",
                "trainName": "LTT CBE EXPRESS",
                "status": "running",
                "delayMinutes": 5,
                "currentLocation": {
                    "stationCode": "PUNE",
                    "stationName": "Pune Junction",
                    "sequence": 4,
                },
                "route": [
                    {
                        "sequence": 4,
                        "stationCode": "PUNE",
                        "scheduledArrival": "17:05",
                        "scheduledDeparture": "17:10",
                    }
                ],
            },
        }

        response = self.client.post("/api/test/collect/11013")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("observation", data)


if __name__ == "__main__":
    unittest.main()

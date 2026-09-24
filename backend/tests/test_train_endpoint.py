"""Integration tests for the main production endpoint GET /api/train/{train_number} (Chunk 7)."""

import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.railway_api import RailwayAPIException


class TestTrainEndpoint(unittest.TestCase):
    """Test suite for GET /api/train/{train_number}."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.api.train_routes.get_live_train_status", new_callable=AsyncMock)
    def test_get_train_endpoint_success_11013(self, mock_get_status):
        """Verify full production pipeline output format for train 11013."""
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

        response = self.client.get("/api/train/11013")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])

        # 1. Train metadata
        self.assertIn("train", data)
        train_info = data["train"]
        self.assertEqual(train_info["train_number"], "11013")
        self.assertEqual(train_info["train_name"], "LTT CBE EXPRESS")
        self.assertEqual(train_info["train_type"], "Express")
        self.assertEqual(train_info["source"], "LTT")
        self.assertEqual(train_info["destination"], "CBE")

        # 2. Live status (current live delay kept separate)
        self.assertIn("live_status", data)
        live_status = data["live_status"]
        self.assertEqual(live_status["current_station_code"], "PUNE")
        self.assertEqual(live_status["current_station_name"], "Pune Junction")
        self.assertEqual(live_status["current_sequence"], 4)
        self.assertEqual(live_status["speed_kmh"], 78.0)
        self.assertEqual(live_status["current_delay_minutes"], 15)

        # 3. Prediction & ETA
        self.assertIn("prediction", data)
        prediction = data["prediction"]
        self.assertEqual(prediction["predicted_delay_minutes"], 0.2)
        self.assertEqual(prediction["next_station"], "Daund Junction")
        self.assertEqual(prediction["next_station_code"], "DD")
        self.assertEqual(prediction["scheduled_arrival"], "18:10")
        self.assertEqual(prediction["expected_arrival"], "18:10")
        self.assertEqual(prediction["scheduled_departure"], "18:15")
        self.assertEqual(prediction["expected_departure"], "18:15")
        self.assertEqual(prediction["destination_eta"], "06:50")

        # 4. Route
        self.assertIn("route", data)
        route_info = data["route"]
        self.assertEqual(route_info["remaining_distance_km"], 1448.0)

        # 5. Raw data excluded from main response
        self.assertNotIn("raw_response", data)
        self.assertNotIn("data", data)

    @patch("app.api.train_routes.get_live_train_status", new_callable=AsyncMock)
    def test_get_train_unauthorized(self, mock_get_status):
        """Verify missing API key returns 401 with clean error."""
        mock_get_status.side_effect = RailwayAPIException(
            message="RailRadar API key is missing. Please set RAILRADAR_API_KEY in backend/.env.",
            status_code=401,
        )

        response = self.client.get("/api/train/11013")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Unauthorized")
        self.assertIn("API key is missing", data["message"])

    @patch("app.api.train_routes.get_live_train_status", new_callable=AsyncMock)
    def test_get_train_not_found(self, mock_get_status):
        """Verify invalid or inactive train returns 404."""
        mock_get_status.side_effect = RailwayAPIException(
            message="Train not found",
            status_code=404,
            details={"error": "Not Found"},
        )

        response = self.client.get("/api/train/99999")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Train not found")

    @patch("app.api.train_routes.get_live_train_status", new_callable=AsyncMock)
    def test_get_train_service_unavailable(self, mock_get_status):
        """Verify upstream 503 returns clean Service Unavailable message."""
        mock_get_status.side_effect = RailwayAPIException(
            message="Upstream server error",
            status_code=503,
        )

        response = self.client.get("/api/train/11013")
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Service Unavailable")
        self.assertEqual(data["message"], "Live railway service is temporarily unavailable.")


if __name__ == "__main__":
    unittest.main()

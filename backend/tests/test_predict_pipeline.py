"""Integration and unit tests for the end-to-end delay prediction pipeline (Chunk 6)."""

import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.railway_api import RailwayAPIException
from app.services.feature_builder import EXPECTED_FEATURES


class TestPredictPipeline(unittest.TestCase):
    """Test suite for GET /api/test/predict/{train_number} and the delay prediction pipeline."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.main.get_live_train_status", new_callable=AsyncMock)
    def test_predict_endpoint_success_11013(self, mock_get_status):
        """Verify full pipeline: RailRadar -> Normalizer -> Feature Builder -> Model -> Prediction."""
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

        response = self.client.get("/api/test/predict/11013")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["train_number"], "11013")

        # Verify all 12 features present in exact order
        features = data["features"]
        self.assertEqual(len(features), 12)
        self.assertEqual(list(features.keys()), EXPECTED_FEATURES)
        self.assertEqual(features["train_number"], "11013")
        self.assertEqual(features["station_code"], "PUNE")

        # Verify prediction payload
        self.assertIn("prediction", data)
        prediction = data["prediction"]
        self.assertIn("predicted_delay_minutes", prediction)
        delay = prediction["predicted_delay_minutes"]
        self.assertIsInstance(delay, float)
        self.assertGreaterEqual(delay, 0.0)

    @patch("app.main.get_live_train_status", new_callable=AsyncMock)
    def test_predict_endpoint_missing_feature(self, mock_get_status):
        """Verify incomplete upstream payload returns structured 400 error."""
        mock_get_status.return_value = {
            "success": True,
            "data": {
                "trainNumber": "11013",
                # Missing route, location, etc.
            },
        }

        response = self.client.get("/api/test/predict/11013")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Unable to generate prediction")
        self.assertIn("missing_features", data)

    @patch("app.main.get_live_train_status", new_callable=AsyncMock)
    def test_predict_endpoint_unauthorized(self, mock_get_status):
        """Verify upstream API authentication failure is propagated cleanly."""
        mock_get_status.side_effect = RailwayAPIException(
            message="RailRadar API key is missing. Please set RAILRADAR_API_KEY in backend/.env.",
            status_code=401,
        )

        response = self.client.get("/api/test/predict/11013")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("API key is missing", data["message"])


if __name__ == "__main__":
    unittest.main()

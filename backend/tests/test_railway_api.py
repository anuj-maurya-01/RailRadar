"""Unit tests for RailRadar Railway API service."""

import unittest
from unittest.mock import patch, MagicMock
import httpx

from app.services.railway_api import (
    RailwayAPIService,
    RailwayAPIException,
    get_railway_service,
)


class TestRailwayAPIService(unittest.TestCase):
    """Test suite for RailwayAPIService."""

    def setUp(self):
        self.service = RailwayAPIService(
            base_url="https://api.railradar.in",
            endpoint_template="/v1/trains/{number}/live",
            api_key="test_api_key_12345",
        )

    def test_url_construction(self):
        """Verify URL is correctly formatted with train number."""
        url = self.service.build_url("11013")
        self.assertEqual(url, "https://api.railradar.in/v1/trains/11013/live")

    def test_url_construction_with_full_endpoint(self):
        """Verify URL construction when endpoint template is an absolute URL."""
        custom_service = RailwayAPIService(
            base_url="https://api.railradar.in",
            endpoint_template="https://custom.railradar.in/api/v1/{number}",
            api_key="key",
        )
        url = custom_service.build_url("12919")
        self.assertEqual(url, "https://custom.railradar.in/api/v1/12919")

    def test_headers_include_bearer_auth(self):
        """Verify Authorization Bearer header is generated properly."""
        headers = self.service._get_headers()
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], "Bearer test_api_key_12345")
        self.assertEqual(headers["Accept"], "application/json")

    def test_missing_api_key_uses_local_dataset_fallback(self):
        """Verify missing API key falls back to the bundled local dataset for demo usage."""
        no_key_service = RailwayAPIService(api_key="")
        fallback_payload = {
            "success": True,
            "data": {
                "trainNumber": "11013",
                "trainName": "COIMBATORE EXP",
                "train": {
                    "number": "11013",
                    "name": "COIMBATORE EXP",
                    "type": "Express",
                    "category": "Mail/Express",
                    "source": {"code": "LTT", "name": "LOKMANYATILAK T"},
                    "destination": {"code": "CBE", "name": "COIMBATORE JN"},
                    "distance": 1501.0,
                },
                "currentLocation": {
                    "stationCode": "PUNE",
                    "stationName": "PUNE JN",
                    "sequence": 4,
                    "status": "departed",
                    "segmentProgress": 0.35,
                    "speedKmh": 72.0,
                    "delayMinutes": 8,
                },
                "previousHalt": {
                    "stationCode": "LTT",
                    "stationName": "LOKMANYATILAK T",
                    "sequence": 1,
                    "scheduledDeparture": "2026-06-22T22:35:00+05:30",
                    "actualDeparture": "2026-06-22T22:42:00+05:30",
                },
                "nextHalt": {
                    "stationCode": "DD",
                    "stationName": "DAUND JN",
                    "sequence": 5,
                    "scheduledArrival": "2026-06-22T23:15:00+05:30",
                    "delayMinutes": 8,
                },
                "route": [
                    {
                        "sequence": 1,
                        "stationCode": "LTT",
                        "stationName": "LOKMANYATILAK T",
                        "scheduledDeparture": "2026-06-22T22:35:00+05:30",
                        "distance": 0.0,
                        "day": 1,
                    },
                    {
                        "sequence": 4,
                        "stationCode": "PUNE",
                        "stationName": "PUNE JN",
                        "scheduledArrival": "2026-06-22T23:50:00+05:30",
                        "scheduledDeparture": "2026-06-22T23:55:00+05:30",
                        "distance": 176.0,
                        "day": 2,
                    },
                    {
                        "sequence": 5,
                        "stationCode": "DD",
                        "stationName": "DAUND JN",
                        "scheduledArrival": "2026-06-23T00:35:00+05:30",
                        "distance": 268.0,
                        "day": 2,
                    },
                ],
                "totalDistance": 1501.0,
                "distanceCovered": 176.0,
                "remainingDistance": 1325.0,
            },
        }

        with patch.object(no_key_service, "_load_local_dataset", return_value=fallback_payload):
            result = no_key_service.get_live_train_status_sync("11013")

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["trainNumber"], "11013")
        self.assertEqual(result["data"]["currentLocation"]["stationCode"], "PUNE")

    def test_missing_train_uses_demo_template_when_dataset_has_no_exact_match(self):
        """Verify unsupported demo numbers still return a valid fallback payload."""
        no_key_service = RailwayAPIService(api_key="")

        result = no_key_service.get_live_train_status_sync("22416")

        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["trainNumber"], "22416")
        self.assertIn("Demo", result["data"]["trainName"])
    def test_handle_response_200_ok(self):
        """Verify valid 200 response preserves actual JSON structure."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "train_number": "11013",
                "train_name": "LTT CBE EXPRESS",
                "current_station": "PUNE",
            },
        }

        result = self.service._handle_response(mock_response, "11013")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["train_name"], "LTT CBE EXPRESS")

    def test_handle_response_401_unauthorized(self):
        """Verify 401 response is converted to RailwayAPIException."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "success": False,
            "error": {"code": "UNAUTHORIZED", "message": "Invalid API Key"},
        }

        with self.assertRaises(RailwayAPIException) as ctx:
            self.service._handle_response(mock_response, "11013")
        self.assertEqual(ctx.exception.status_code, 401)
        self.assertIn("Unauthorized", ctx.exception.message)

    def test_handle_response_404_not_found(self):
        """Verify 404 response is handled gracefully."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.json.return_value = {"success": False, "error": {"message": "Train not found"}}

        with self.assertRaises(RailwayAPIException) as ctx:
            self.service._handle_response(mock_response, "99999")
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("99999", ctx.exception.message)

    def test_handle_response_429_rate_limit(self):
        """Verify 429 response is handled gracefully."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.json.return_value = {"success": False}

        with self.assertRaises(RailwayAPIException) as ctx:
            self.service._handle_response(mock_response, "11013")
        self.assertEqual(ctx.exception.status_code, 429)

    def test_handle_response_500_server_error(self):
        """Verify upstream 500 error maps to 502 with safe message."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}

        with self.assertRaises(RailwayAPIException) as ctx:
            self.service._handle_response(mock_response, "11013")
        self.assertEqual(ctx.exception.status_code, 502)
        self.assertIn("upstream server error", ctx.exception.message)


if __name__ == "__main__":
    unittest.main()

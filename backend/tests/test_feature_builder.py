"""Unit and integration tests for ML feature builder service (Chunk 5)."""

import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.feature_builder import (
    build_ml_features,
    time_to_minutes,
    map_train_type,
    calculate_scheduled_travel_time,
    calculate_day,
    calculate_scheduled_remaining_time,
    validate_ml_features,
    FeatureBuilderError,
    EXPECTED_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)
from app.services.railway_api import RailwayAPIException


class TestFeatureBuilder(unittest.TestCase):
    """Test suite for feature builder components."""

    def test_time_to_minutes(self):
        """Verify time_to_minutes conversion with standard, midnight, and invalid values."""
        # Standard examples from requirements
        self.assertEqual(time_to_minutes("18:42"), 1122)
        self.assertEqual(time_to_minutes("00:30"), 30)
        self.assertEqual(time_to_minutes("23:15"), 1395)

        # Midnight bounds
        self.assertEqual(time_to_minutes("00:00"), 0)
        self.assertEqual(time_to_minutes("23:59"), 1439)

        # Edge & invalid cases (must not invent missing times)
        self.assertIsNone(time_to_minutes(None))
        self.assertIsNone(time_to_minutes(""))
        self.assertIsNone(time_to_minutes("   "))
        self.assertIsNone(time_to_minutes("invalid:time"))
        self.assertIsNone(time_to_minutes("25:00"))
        self.assertIsNone(time_to_minutes("12:60"))

        # ISO 8601 timestamps
        self.assertEqual(time_to_minutes("2026-06-22T23:55:00+05:30"), 1435)
        self.assertEqual(time_to_minutes("2026-06-23T00:05:00+05:30"), 5)

        # 12-hour format
        self.assertEqual(time_to_minutes("11:15 PM"), 1395)
        self.assertEqual(time_to_minutes("12:30 AM"), 30)

    def test_calculate_scheduled_travel_time_standard_and_midnight(self):
        """Verify travel time calculation including crossing midnight."""
        # Standard within same day
        self.assertEqual(calculate_scheduled_travel_time(600, 660), 60.0)

        # Crossing midnight (23:50 -> 00:20 = 30 minutes, not -1410)
        t_2350 = time_to_minutes("23:50")  # 1430
        t_0020 = time_to_minutes("00:20")  # 20
        self.assertEqual(calculate_scheduled_travel_time(t_2350, t_0020), 30.0)

        # Missing values must return None
        self.assertIsNone(calculate_scheduled_travel_time(None, 60))
        self.assertIsNone(calculate_scheduled_travel_time(60, None))
        self.assertIsNone(calculate_scheduled_travel_time(None, None))

    def test_map_train_type(self):
        """Verify train type mapping adheres to encoder classes ('Express', 'Superfast')."""
        self.assertEqual(map_train_type("Superfast Express"), "Superfast")
        self.assertEqual(map_train_type(None, "SUPERFAST"), "Superfast")
        self.assertEqual(map_train_type("Rajdhani Express"), "Superfast")
        self.assertEqual(map_train_type("Vande Bharat"), "Superfast")
        self.assertEqual(map_train_type("Express"), "Express")
        self.assertEqual(map_train_type("Mail"), "Express")
        self.assertEqual(map_train_type("Passenger"), "Express")
        self.assertEqual(map_train_type(None, None), "Express")

    def test_calculate_day(self):
        """Verify day determination from route day or date difference."""
        # Direct day value
        self.assertEqual(calculate_day("2026-06-22", "2026-06-23T10:00:00", stop_day_val=2), 2)
        # Offset calculation
        self.assertEqual(calculate_day("2026-06-22", "2026-06-24T05:00:00", stop_day_val=None), 3)
        # Default fallback
        self.assertEqual(calculate_day(None, None, None), 1)

    def test_calculate_scheduled_remaining_time(self):
        """Verify remaining time calculation to destination."""
        curr = {"sequence": 5, "scheduledDeparture": "10:00", "day": 1}
        dest = {"sequence": 10, "scheduledArrival": "14:30", "day": 1}
        self.assertEqual(calculate_scheduled_remaining_time(curr, dest), 270.0)

        # Already at destination
        at_dest = {"sequence": 10, "scheduledArrival": "14:30", "day": 1}
        self.assertEqual(calculate_scheduled_remaining_time(at_dest, dest), 0.0)

        # Multi-day journey
        curr_d1 = {"sequence": 2, "scheduledDeparture": "22:00", "day": 1}
        dest_d2 = {"sequence": 8, "scheduledArrival": "06:00", "day": 2}
        self.assertEqual(calculate_scheduled_remaining_time(curr_d1, dest_d2), 480.0)

    def test_validate_ml_features(self):
        """Verify validation checks all 12 features, types, and schema."""
        valid_features = {
            "train_number": "11013",
            "train_type": "Express",
            "station_code": "PUNE",
            "sno": 4,
            "day": 1,
            "distance_km": 192.0,
            "arrival_minutes": 1025.0,
            "departure_minutes": 1030.0,
            "next_arrival_minutes": 1085.0,
            "scheduled_travel_time": 55.0,
            "remaining_distance_km": 1448.0,
            "scheduled_remaining_time": 1850.0,
        }
        # Should not raise
        validate_ml_features(valid_features)

        # Missing feature
        incomplete = valid_features.copy()
        del incomplete["distance_km"]
        with self.assertRaises(FeatureBuilderError) as ctx:
            validate_ml_features(incomplete)
        self.assertIn("distance_km", str(ctx.exception))

        # Extra unexpected feature
        extra = valid_features.copy()
        extra["unwanted_feature"] = 123
        with self.assertRaises(FeatureBuilderError) as ctx:
            validate_ml_features(extra)
        self.assertIn("unwanted_feature", str(ctx.exception))

        # Invalid categorical type
        invalid_cat = valid_features.copy()
        invalid_cat["station_code"] = ""
        with self.assertRaises(FeatureBuilderError):
            validate_ml_features(invalid_cat)

        # Invalid numerical type
        invalid_num = valid_features.copy()
        invalid_num["sno"] = "fourth"
        with self.assertRaises(FeatureBuilderError):
            validate_ml_features(invalid_num)

    def test_build_ml_features_complete_payload(self):
        """Verify build_ml_features returns exact 12-feature dictionary with expected order."""
        normalized_data = {
            "train_number": "11013",
            "train_name": "LTT CBE EXPRESS",
            "train_type": "EXPRESS",
            "train_category": "Mail/Express",
            "current_station_name": "Pune Junction",
            "current_station_code": "PUNE",
            "current_sequence": 4,
            "journey_date": "2026-06-22",
            "total_distance_km": 1640.0,
            "distance_covered_km": 192.0,
            "remaining_distance_km": 1448.0,
            "previous_scheduled_arrival": "17:05",
            "previous_scheduled_departure": "17:10",
            "next_station_code": "DD",
            "next_scheduled_arrival": "18:10",
            "route": [
                {
                    "sequence": 1,
                    "stationCode": "LTT",
                    "scheduledDeparture": "10:35",
                    "distance": 0.0,
                    "day": 1,
                },
                {
                    "sequence": 4,
                    "stationCode": "PUNE",
                    "scheduledArrival": "17:05",
                    "scheduledDeparture": "17:10",
                    "distance": 192.0,
                    "day": 1,
                },
                {
                    "sequence": 5,
                    "stationCode": "DD",
                    "scheduledArrival": "18:10",
                    "scheduledDeparture": "18:15",
                    "distance": 268.0,
                    "day": 1,
                },
                {
                    "sequence": 28,
                    "stationCode": "CBE",
                    "scheduledArrival": "06:50",
                    "distance": 1640.0,
                    "day": 2,
                },
            ],
        }

        features = build_ml_features(normalized_data)

        self.assertIsInstance(features, dict)
        self.assertEqual(len(features), 12)
        self.assertEqual(list(features.keys()), EXPECTED_FEATURES)

        self.assertEqual(features["train_number"], "11013")
        self.assertEqual(features["train_type"], "Express")
        self.assertEqual(features["station_code"], "PUNE")
        self.assertEqual(features["sno"], 4)
        self.assertEqual(features["day"], 1)
        self.assertEqual(features["distance_km"], 192.0)
        self.assertEqual(features["arrival_minutes"], 1025.0)  # 17 * 60 + 5
        self.assertEqual(features["departure_minutes"], 1030.0)  # 17 * 60 + 10
        self.assertEqual(features["next_arrival_minutes"], 1090.0)  # 18 * 60 + 10
        self.assertEqual(features["scheduled_travel_time"], 65.0)  # 1090 - 1025
        self.assertEqual(features["remaining_distance_km"], 1448.0)
        self.assertGreater(features["scheduled_remaining_time"], 0.0)


class TestFeaturesEndpoint(unittest.TestCase):
    """Integration test suite for GET /api/test/features/{train_number}."""

    def setUp(self):
        self.client = TestClient(app)

    @patch("app.main.get_live_train_status", new_callable=AsyncMock)
    def test_get_features_endpoint_success(self, mock_get_status):
        """Verify GET /api/test/features/{train_number} returns exactly 12 features."""
        mock_get_status.return_value = {
            "success": True,
            "data": {
                "train_number": "11013",
                "train_name": "LTT CBE EXPRESS",
                "train_type": "EXPRESS",
                "current_station": {
                    "code": "PUNE",
                    "name": "Pune Jn",
                    "sequence": 4,
                    "scheduled_arrival": "17:05",
                    "scheduled_departure": "17:10",
                },
                "next_station": {
                    "code": "DD",
                    "name": "Daund Jn",
                    "scheduled_arrival": "18:10",
                },
                "total_distance": 1640.0,
                "distance_covered": 192.0,
                "remaining_distance": 1448.0,
                "route": [
                    {
                        "sequence": 1,
                        "code": "LTT",
                        "scheduled_departure": "10:35",
                        "distance": 0.0,
                        "day": 1,
                    },
                    {
                        "sequence": 4,
                        "code": "PUNE",
                        "scheduled_arrival": "17:05",
                        "scheduled_departure": "17:10",
                        "distance": 192.0,
                        "day": 1,
                    },
                    {
                        "sequence": 5,
                        "code": "DD",
                        "scheduled_arrival": "18:10",
                        "scheduled_departure": "18:15",
                        "distance": 268.0,
                        "day": 1,
                    },
                    {
                        "sequence": 28,
                        "code": "CBE",
                        "scheduled_arrival": "06:50",
                        "distance": 1640.0,
                        "day": 2,
                    },
                ],
            },
        }

        response = self.client.get("/api/test/features/11013")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["train_number"], "11013")
        self.assertIn("features", data)

        features = data["features"]
        self.assertEqual(len(features), 12)
        self.assertEqual(list(features.keys()), EXPECTED_FEATURES)
        self.assertEqual(features["train_number"], "11013")
        self.assertEqual(features["station_code"], "PUNE")

    @patch("app.main.get_live_train_status", new_callable=AsyncMock)
    def test_get_features_endpoint_api_error(self, mock_get_status):
        """Verify upstream RailwayAPIException is handled cleanly."""
        mock_get_status.side_effect = RailwayAPIException(
            message="RailRadar API key is missing.",
            status_code=401,
            details={"error": "unauthorized"},
        )

        response = self.client.get("/api/test/features/11013")
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("API key is missing", data["message"])


if __name__ == "__main__":
    unittest.main()

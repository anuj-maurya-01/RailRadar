"""Unit tests for train data normalization service."""

import unittest
from app.services.train_data_normalizer import (
    normalize_train_status,
    normalize_time,
    normalize_distance,
    normalize_float,
    normalize_int,
)


class TestTrainDataNormalizer(unittest.TestCase):
    """Test suite for train_data_normalizer service."""

    def test_normalize_time_edge_cases(self):
        """Verify time normalization across various formats and edge cases."""
        self.assertIsNone(normalize_time(None))
        self.assertIsNone(normalize_time(""))
        self.assertIsNone(normalize_time("   "))
        self.assertIsNone(normalize_time("invalid_time"))
        self.assertIsNone(normalize_time(12345))

        # ISO 8601 strings
        self.assertEqual(normalize_time("2026-06-22T23:55:00+05:30"), "23:55")
        self.assertEqual(normalize_time("2026-06-23T00:07:00+05:30"), "00:07")
        self.assertEqual(normalize_time("2026-06-23T00:00:00Z"), "00:00")

        # Standard 24h strings
        self.assertEqual(normalize_time("14:30"), "14:30")
        self.assertEqual(normalize_time("14:30:15"), "14:30")
        self.assertEqual(normalize_time("00:00"), "00:00")

        # 12h AM/PM strings
        self.assertEqual(normalize_time("11:55 PM"), "23:55")
        self.assertEqual(normalize_time("12:05 AM"), "00:05")
        self.assertEqual(normalize_time("12:30 PM"), "12:30")

    def test_normalize_distance_edge_cases(self):
        """Verify distance normalization across various formats and units."""
        self.assertIsNone(normalize_distance(None))
        self.assertIsNone(normalize_distance(""))
        self.assertIsNone(normalize_distance("unknown"))

        self.assertEqual(normalize_distance(123), 123.0)
        self.assertEqual(normalize_distance(123.5), 123.5)
        self.assertEqual(normalize_distance("123 km"), 123.0)
        self.assertEqual(normalize_distance("123 kms"), 123.0)
        self.assertEqual(normalize_distance("  1640.5 KM  "), 1640.5)

    def test_empty_or_invalid_raw_response(self):
        """Verify normalizer returns clean None-filled schema on empty or non-dict input."""
        res = normalize_train_status({})
        self.assertIsInstance(res, dict)
        self.assertIn("train_number", res)
        self.assertIsNone(res["train_number"])
        self.assertIn("previous_scheduled_arrival", res)
        self.assertIsNone(res["previous_scheduled_arrival"])
        self.assertIn("next_station_code", res)
        self.assertIsNone(res["next_station_code"])
        self.assertIn("total_distance_km", res)
        self.assertIsNone(res["total_distance_km"])

        res_none = normalize_train_status(None)
        self.assertIsInstance(res_none, dict)
        self.assertIsNone(res_none["train_number"])

    def test_missing_nested_structures(self):
        """Verify that missing currentLocation, previousHalt, nextHalt, or route do not crash."""
        partial_payload = {
            "data": {
                "trainNumber": "11013",
                "trainName": "LTT CBE EXPRESS",
                "status": "running",
                # missing train, currentLocation, previousHalt, nextHalt, route
            }
        }
        res = normalize_train_status(partial_payload)
        self.assertEqual(res["train_number"], "11013")
        self.assertEqual(res["train_name"], "LTT CBE EXPRESS")
        self.assertEqual(res["current_status"], "running")
        self.assertIsNone(res["current_station_code"])
        self.assertIsNone(res["previous_station_code"])
        self.assertIsNone(res["next_station_code"])
        self.assertIsNone(res["route"])

    def test_full_railradar_sample(self):
        """Verify normalization of a full realistic RailRadar live train response."""
        full_payload = {
            "success": True,
            "data": {
                "trainNumber": "12919",
                "trainName": "Malwa SF Express",
                "startDate": "2026-06-22",
                "status": "running",
                "delayMinutes": 12,
                "train": {
                    "number": "12919",
                    "name": "Malwa SF Express",
                    "type": "Superfast Express",
                    "category": "Superfast",
                    "source": {"code": "INDB", "name": "Indore Junction"},
                    "destination": {"code": "SVDK", "name": "Shri Mata Vaishno Devi Katra"},
                    "distance": 1640,
                },
                "currentLocation": {
                    "stationCode": "UJN",
                    "stationName": "Ujjain Junction",
                    "sequence": 2,
                    "status": "departed",
                    "segmentProgress": 0.45,
                    "speedKmh": 65.5,
                },
                "previousHalt": {
                    "stationCode": "INDB",
                    "stationName": "Indore Junction",
                    "sequence": 1,
                    "distance": 0,
                },
                "nextHalt": {
                    "stationCode": "UJN",
                    "stationName": "Ujjain Junction",
                    "sequence": 2,
                    "distance": 55,
                    "delayMinutes": 12,
                },
                "route": [
                    {
                        "sequence": 1,
                        "stationCode": "INDB",
                        "stationName": "Indore Junction",
                        "scheduledDeparture": "2026-06-22T23:55:00+05:30",
                        "actualDeparture": "2026-06-23T00:07:00+05:30",
                        "distance": 0,
                        "speedToNextStationKmph": 55,
                    },
                    {
                        "sequence": 2,
                        "stationCode": "UJN",
                        "stationName": "Ujjain Junction",
                        "scheduledArrival": "2026-06-23T00:55:00+05:30",
                        "actualArrival": "2026-06-23T01:07:00+05:30",
                        "distance": 55,
                        "speedToNextStationKmph": 60,
                    },
                ],
            },
        }

        res = normalize_train_status(full_payload)

        # Train information
        self.assertEqual(res["train_number"], "12919")
        self.assertEqual(res["train_name"], "Malwa SF Express")
        self.assertEqual(res["train_type"], "Superfast Express")
        self.assertEqual(res["train_category"], "Superfast")
        self.assertEqual(res["source_station"], "INDB")
        self.assertEqual(res["destination_station"], "SVDK")

        # Current train status
        self.assertEqual(res["current_station_code"], "UJN")
        self.assertEqual(res["current_station_name"], "Ujjain Junction")
        self.assertEqual(res["current_sequence"], 2)
        self.assertEqual(res["current_status"], "departed")
        self.assertEqual(res["segment_progress"], 0.45)
        self.assertEqual(res["speed_kmh"], 65.5)
        self.assertEqual(res["delay_minutes"], 12)

        # Previous halt
        self.assertEqual(res["previous_station_code"], "INDB")
        self.assertEqual(res["previous_station_name"], "Indore Junction")
        self.assertIsNone(res["previous_scheduled_arrival"])
        self.assertEqual(res["previous_scheduled_departure"], "23:55")
        self.assertEqual(res["previous_actual_departure"], "00:07")

        # Next halt
        self.assertEqual(res["next_station_code"], "UJN")
        self.assertEqual(res["next_station_name"], "Ujjain Junction")
        self.assertEqual(res["next_sequence"], 2)
        self.assertEqual(res["next_scheduled_arrival"], "00:55")
        self.assertEqual(res["next_estimated_arrival"], "01:07")
        self.assertEqual(res["next_delay_minutes"], 12)
        self.assertEqual(res["distance_to_next_station_km"], 30.25)
        self.assertEqual(res["speed_to_next_station_kmph"], 60.0)

        # Journey information
        self.assertEqual(res["journey_date"], "2026-06-22")
        self.assertEqual(res["total_distance_km"], 1640.0)
        self.assertEqual(res["distance_covered_km"], 24.75)
        self.assertEqual(res["remaining_distance_km"], 1615.25)
        self.assertIsNotNone(res["route"])
        self.assertEqual(len(res["route"]), 2)


if __name__ == "__main__":
    unittest.main()

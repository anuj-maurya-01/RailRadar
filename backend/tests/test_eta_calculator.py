"""Unit tests for ETA Calculator Service (Chunk 7)."""

import unittest
from app.services.eta_calculator import (
    add_minutes_to_time,
    calculate_expected_arrival,
    calculate_expected_departure,
    calculate_destination_eta,
    calculate_train_eta_summary,
)


class TestETACalculator(unittest.TestCase):
    """Test suite for time arithmetic and ETA calculations."""

    def test_add_minutes_standard(self):
        """Verify adding minutes within the same day."""
        # Prompt examples
        self.assertEqual(add_minutes_to_time("18:42", 27), "19:09")
        self.assertEqual(add_minutes_to_time("10:00", 15), "10:15")
        self.assertEqual(add_minutes_to_time("00:15", 45), "01:00")
        self.assertEqual(add_minutes_to_time("14:30:00", 20), "14:50")

    def test_add_minutes_midnight_crossing(self):
        """Verify crossing midnight correctly wraps around 24 hours."""
        # Prompt example: 23:50 + 30 minutes = 00:20
        self.assertEqual(add_minutes_to_time("23:50", 30), "00:20")
        self.assertEqual(add_minutes_to_time("23:45", 15), "00:00")
        self.assertEqual(add_minutes_to_time("23:55", 70), "01:05")

    def test_add_minutes_invalid_inputs(self):
        """Verify invalid or missing inputs safely return None without crashing."""
        self.assertIsNone(add_minutes_to_time(None, 27))
        self.assertIsNone(add_minutes_to_time("", 27))
        self.assertIsNone(add_minutes_to_time("invalid", 27))
        self.assertIsNone(add_minutes_to_time("25:00", 27))
        self.assertIsNone(add_minutes_to_time("18:42", None))

    def test_calculate_expected_arrival(self):
        """Verify calculation of next station expected arrival."""
        self.assertEqual(calculate_expected_arrival("18:42", 27), "19:09")
        self.assertEqual(calculate_expected_arrival("23:50", 30), "00:20")
        self.assertIsNone(calculate_expected_arrival(None, 27))

    def test_calculate_expected_departure(self):
        """Verify calculation of next station expected departure."""
        self.assertEqual(calculate_expected_departure("18:45", 27), "19:12")
        self.assertIsNone(calculate_expected_departure(None, 27))

    def test_calculate_destination_eta(self):
        """Verify destination ETA calculation."""
        # Prompt example: 22:30 + 27 minutes = 22:57
        self.assertEqual(calculate_destination_eta("22:30", 27), "22:57")
        self.assertIsNone(calculate_destination_eta(None, 27))

    def test_calculate_train_eta_summary_complete(self):
        """Verify complete ETA summary construction from normalized data."""
        normalized_data = {
            "train_number": "11013",
            "destination_station": "CBE",
            "next_station_code": "DD",
            "next_station_name": "Daund Junction",
            "next_sequence": 5,
            "next_scheduled_arrival": "18:10",
            "route": [
                {
                    "sequence": 4,
                    "stationCode": "PUNE",
                    "stationName": "Pune Junction",
                    "scheduledArrival": "17:05",
                    "scheduledDeparture": "17:10",
                },
                {
                    "sequence": 5,
                    "stationCode": "DD",
                    "stationName": "Daund Junction",
                    "scheduledArrival": "18:10",
                    "scheduledDeparture": "18:15",
                },
                {
                    "sequence": 28,
                    "stationCode": "CBE",
                    "stationName": "Coimbatore Main Junction",
                    "scheduledArrival": "06:50",
                },
            ],
        }

        # With 15 minutes delay
        summary = calculate_train_eta_summary(normalized_data, 15.0)

        self.assertEqual(summary["predicted_delay_minutes"], 15.0)
        self.assertEqual(summary["next_station"], "Daund Junction")
        self.assertEqual(summary["next_station_code"], "DD")
        self.assertEqual(summary["scheduled_arrival"], "18:10")
        self.assertEqual(summary["expected_arrival"], "18:25")
        self.assertEqual(summary["scheduled_departure"], "18:15")
        self.assertEqual(summary["expected_departure"], "18:30")
        self.assertEqual(summary["destination_eta"], "07:05")

    def test_calculate_train_eta_summary_missing_destination(self):
        """Verify missing destination scheduled arrival provides null and explanation."""
        normalized_data = {
            "train_number": "11013",
            "destination_station": "CBE",
            "next_station_code": "DD",
            "next_station_name": "Daund Junction",
            "next_sequence": 5,
            "next_scheduled_arrival": "18:10",
            "route": [
                {
                    "sequence": 5,
                    "stationCode": "DD",
                    "scheduledArrival": "18:10",
                },
            ],
        }

        summary = calculate_train_eta_summary(normalized_data, 10.0)
        self.assertIsNone(summary["destination_eta"])
        self.assertIn("destination_eta_explanation", summary)


if __name__ == "__main__":
    unittest.main()

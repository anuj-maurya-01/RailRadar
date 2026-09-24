"""Unit tests for ML model loading, verification, and ETA prediction (Chunk 6)."""

import unittest
from app.services.eta_predictor import (
    ETAPredictorService,
    get_predictor,
    predict_delay,
    ETAPredictionError,
)


class TestETAPredictor(unittest.TestCase):
    """Test suite for the ETA predictor service."""

    @classmethod
    def setUpClass(cls):
        cls.predictor = get_predictor()

    def test_predictor_singleton(self):
        """Verify that get_predictor returns the same singleton instance."""
        p1 = get_predictor()
        p2 = get_predictor()
        self.assertIs(p1, p2)
        self.assertTrue(p1._is_loaded)

    def test_model_and_encoder_types(self):
        """Verify the loaded model and encoder match expected types and config."""
        self.assertIsNotNone(self.predictor.model)
        self.assertEqual(type(self.predictor.model).__name__, "HistGradientBoostingRegressor")
        self.assertIsNotNone(self.predictor.encoder)
        self.assertEqual(type(self.predictor.encoder).__name__, "OneHotEncoder")
        self.assertEqual(len(self.predictor.all_features), 12)
        self.assertEqual(len(self.predictor.categorical_features), 3)
        self.assertEqual(len(self.predictor.numerical_features), 9)
        self.assertEqual(self.predictor.encoded_features_count, 475)

    def test_sample_prediction_single(self):
        """Verify single-sample prediction execution and dictionary output format."""
        sample = {
            "train_number": "11013",
            "train_type": "Express",
            "station_code": "PUNE",
            "sno": 4,
            "day": 1,
            "distance_km": 192.0,
            "arrival_minutes": 1025.0,
            "departure_minutes": 1030.0,
            "next_arrival_minutes": 1090.0,
            "scheduled_travel_time": 65.0,
            "remaining_distance_km": 1448.0,
            "scheduled_remaining_time": 820.0,
        }
        result = predict_delay(sample)
        self.assertIsInstance(result, dict)
        self.assertIn("predicted_delay_minutes", result)
        self.assertIsInstance(result["predicted_delay_minutes"], float)
        self.assertGreaterEqual(result["predicted_delay_minutes"], 0.0)

        # Test as_dict=False
        float_res = predict_delay(sample, as_dict=False)
        self.assertIsInstance(float_res, float)
        self.assertEqual(float_res, result["predicted_delay_minutes"])

    def test_sample_prediction_batch(self):
        """Verify batch prediction execution and output format."""
        sample = {
            "train_number": "11013",
            "train_type": "Express",
            "station_code": "PUNE",
            "sno": 4,
            "day": 1,
            "distance_km": 192.0,
            "arrival_minutes": 1025.0,
            "departure_minutes": 1030.0,
            "next_arrival_minutes": 1090.0,
            "scheduled_travel_time": 65.0,
            "remaining_distance_km": 1448.0,
            "scheduled_remaining_time": 820.0,
        }
        batch = [sample, sample]
        results = predict_delay(batch)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], dict)
        self.assertIn("predicted_delay_minutes", results[0])

    def test_missing_feature_error(self):
        """Verify that missing required features raises structured ETAPredictionError."""
        incomplete_sample = {
            "train_number": "11013",
            "train_type": "Express",
        }
        with self.assertRaises(ETAPredictionError) as ctx:
            predict_delay(incomplete_sample)
        self.assertTrue(len(ctx.exception.missing_features) > 0)
        self.assertIn("station_code", ctx.exception.missing_features)

    def test_null_feature_error(self):
        """Verify that None values in required features raise ETAPredictionError."""
        null_sample = {
            "train_number": "11013",
            "train_type": "Express",
            "station_code": "PUNE",
            "sno": 4,
            "day": 1,
            "distance_km": 192.0,
            "arrival_minutes": 1025.0,
            "departure_minutes": 1030.0,
            "next_arrival_minutes": 1090.0,
            "scheduled_travel_time": 65.0,
            "remaining_distance_km": None,
            "scheduled_remaining_time": 820.0,
        }
        with self.assertRaises(ETAPredictionError) as ctx:
            predict_delay(null_sample)
        self.assertIn("remaining_distance_km", ctx.exception.missing_features)

    def test_unknown_categorical_handling(self):
        """Verify that unknown train/station categories are handled gracefully without crashing."""
        sample_unknown = {
            "train_number": "99999",  # unknown train number
            "train_type": "Superfast",
            "station_code": "ZZZZ",  # unknown station
            "sno": 1,
            "day": 1,
            "distance_km": 0.0,
            "arrival_minutes": 360,
            "departure_minutes": 365,
            "next_arrival_minutes": 420,
            "scheduled_travel_time": 60.0,
            "remaining_distance_km": 500.0,
            "scheduled_remaining_time": 300.0,
        }
        result = predict_delay(sample_unknown)
        self.assertIsInstance(result, dict)
        self.assertIn("predicted_delay_minutes", result)
        self.assertIsInstance(result["predicted_delay_minutes"], float)

    def test_internal_verify_model(self):
        """Verify the internal verification helper returns verified status."""
        verification = self.predictor.verify_model()
        self.assertEqual(verification["status"], "verified")
        self.assertEqual(verification["model_type"], "HistGradientBoostingRegressor")
        self.assertEqual(verification["expected_raw_features"], 12)
        self.assertIn("sample_prediction_minutes", verification)


if __name__ == "__main__":
    unittest.main()

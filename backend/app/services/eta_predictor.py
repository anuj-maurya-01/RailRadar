import json
import logging
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Compatibility shim: models pickled with older scikit-learn (e.g. 1.6.1) reference
# the Cython loss extension module as top-level '_loss' instead of 'sklearn._loss._loss'.
try:
    import sklearn._loss._loss
    sys.modules.setdefault("_loss", sklearn._loss._loss)
except (ImportError, AttributeError):
    pass

import joblib
import numpy as np
import pandas as pd

from app.config import ETA_ENCODER_PATH, ETA_MODEL_PATH, FEATURE_CONFIG_PATH

logger = logging.getLogger(__name__)


class ETAPredictionError(Exception):
    """Custom exception raised when ML prediction cannot be completed."""

    def __init__(
        self,
        message: str,
        missing_features: Optional[List[str]] = None,
        reason: Optional[str] = None,
        source_field: Optional[str] = None,
        status_code: int = 400,
    ):
        self.message = message
        self.missing_features = missing_features or []
        self.reason = reason
        self.source_field = source_field
        self.status_code = status_code
        super().__init__(message)


class ETAPredictorService:
    """Service responsible for loading the trained ML model, encoder,
    and feature configuration once and performing ETA delay predictions.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._is_loaded = False
        return cls._instance

    def __init__(
        self,
        model_path: Union[str, Path] = ETA_MODEL_PATH,
        encoder_path: Union[str, Path] = ETA_ENCODER_PATH,
        config_path: Union[str, Path] = FEATURE_CONFIG_PATH,
    ):
        if self._is_loaded:
            return

        self.model_path = Path(model_path)
        self.encoder_path = Path(encoder_path)
        self.config_path = Path(config_path)

        self.model = None
        self.encoder = None
        self.config: Dict[str, Any] = {}

        self.categorical_features: List[str] = []
        self.numerical_features: List[str] = []
        self.all_features: List[str] = []
        self.target_column: str = "average_delay_minutes"
        self.model_type: str = ""
        self.encoded_features_count: int = 0

        self._load_artifacts()
        self._is_loaded = True

    def _load_artifacts(self) -> None:
        """Load feature configuration, ML model, and categorical encoder from disk."""
        # 1. Load Feature Configuration
        if not self.config_path.exists():
            raise FileNotFoundError(f"Feature config not found at: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.categorical_features = self.config.get("categorical_features", [])
        self.numerical_features = self.config.get("numerical_features", [])
        self.all_features = self.config.get("all_features", [])
        self.target_column = self.config.get("target_column", "average_delay_minutes")
        self.model_type = self.config.get("model_type", "HistGradientBoostingRegressor")
        self.encoded_features_count = self.config.get("encoded_features", 475)

        # 2. Load Trained Model
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")

        try:
            import sklearn._loss._loss
            sys.modules.setdefault("_loss", sklearn._loss._loss)
        except (ImportError, AttributeError):
            pass

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
            self.model = joblib.load(self.model_path)

        # 3. Load Categorical Encoder
        if not self.encoder_path.exists():
            raise FileNotFoundError(f"Encoder file not found at: {self.encoder_path}")
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
            self.encoder = joblib.load(self.encoder_path)

        logger.info("ML Model, Encoder, and Feature Configuration loaded successfully.")

    def predict_delay(
        self,
        features: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
        as_dict: bool = True,
    ) -> Union[Dict[str, float], List[Dict[str, float]], float, List[float]]:
        """Predict expected delay in minutes for the given feature set.

        Parameters
        ----------
        features : dict, list of dicts, or pandas DataFrame
            Input containing the required 12 categorical and numerical features.
        as_dict : bool, default True
            If True, returns {"predicted_delay_minutes": float}.
            If False, returns float.

        Returns
        -------
        dict, list of dict, float, or list of float
            Predicted delay in minutes.
        """
        if not self._is_loaded or self.model is None or self.encoder is None:
            raise RuntimeError("Model and artifacts have not been loaded.")

        # Determine single vs batch input
        is_single = False
        if isinstance(features, dict):
            df = pd.DataFrame([features])
            is_single = True
        elif isinstance(features, list):
            df = pd.DataFrame(features)
        elif isinstance(features, pd.DataFrame):
            df = features.copy()
        else:
            raise TypeError(f"Unsupported features type: {type(features)}. Expected dict, list, or DataFrame.")

        # 1. Validate that all required features are present and non-null
        missing_or_null: List[str] = []
        for col in self.all_features:
            if col not in df.columns:
                missing_or_null.append(col)
            elif df[col].isnull().any():
                missing_or_null.append(col)

        if missing_or_null:
            raise ETAPredictionError(
                message="Unable to generate prediction due to missing or null required features.",
                missing_features=missing_or_null,
                reason=f"The following required model features are missing or null: {missing_or_null}",
                status_code=400,
            )

        # 2. Extract and format categorical features as string
        cat_df = df[self.categorical_features].astype(str)

        # 3. Apply saved OneHotEncoder to categorical columns
        try:
            encoded_cats = self.encoder.transform(cat_df)
            if hasattr(encoded_cats, "toarray"):
                encoded_cats = encoded_cats.toarray()
        except Exception as exc:
            logger.error(f"Error encoding categorical features: {exc}")
            raise ETAPredictionError(
                message="Live station/train category is not present in the trained encoder.",
                reason=str(exc),
                status_code=400,
            )

        # 4. Extract numerical features and convert to float array
        try:
            num_vals = df[self.numerical_features].astype(float).to_numpy()
        except Exception as exc:
            raise ETAPredictionError(
                message=f"Error parsing numerical features to numeric values: {str(exc)}",
                reason=str(exc),
                status_code=400,
            )

        # 5. Combine encoded categorical features with numerical features in training order
        combined_features = np.hstack([encoded_cats, num_vals])

        # 6. Execute prediction with loaded HistGradientBoostingRegressor
        try:
            raw_predictions = self.model.predict(combined_features)
        except Exception as exc:
            raise ETAPredictionError(
                message=f"Model execution error: {str(exc)}",
                reason=str(exc),
                status_code=500,
            )

        # 7. Sensibly handle negative predicted delay and format output
        def _format_delay(raw_val: float) -> float:
            # In railway operations, delay represents minutes behind schedule.
            # If the model predicts negative delay (running ahead of schedule),
            # it is sensibly clamped to 0.0 minutes (on-time arrival with 0 delay).
            val_float = float(raw_val)
            if val_float < 0.0:
                return 0.0
            return round(val_float, 1)

        if is_single:
            formatted = _format_delay(raw_predictions[0])
            if as_dict:
                return {"predicted_delay_minutes": formatted}
            return formatted

        batch_formatted = [_format_delay(p) for p in raw_predictions]
        if as_dict:
            return [{"predicted_delay_minutes": p} for p in batch_formatted]
        return batch_formatted

    def verify_model(self) -> Dict[str, Any]:
        """Perform internal verification that model, encoder, and config are loaded,
        and execute a sample prediction.
        """
        logger.info("Model loaded successfully")
        logger.info("Encoder loaded successfully")
        logger.info("Feature configuration loaded successfully")

        # Construct a representative sample input matching model expectations
        sample_input = {
            "train_number": str(self.encoder.categories_[0][0]),
            "train_type": str(self.encoder.categories_[1][0]),
            "station_code": str(self.encoder.categories_[2][0]),
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

        sample_res = self.predict_delay(sample_input, as_dict=True)
        sample_delay = (
            sample_res["predicted_delay_minutes"]
            if isinstance(sample_res, dict)
            else float(sample_res)
        )
        logger.info(f"Sample prediction succeeded: {sample_delay:.2f} minutes")

        return {
            "status": "verified",
            "model_type": self.model_type,
            "expected_raw_features": len(self.all_features),
            "categorical_features": self.categorical_features,
            "numerical_features": self.numerical_features,
            "encoded_features_count": self.encoded_features_count,
            "sample_prediction_minutes": sample_delay,
        }


# Centralized singleton accessor
_predictor_instance: Union[ETAPredictorService, None] = None


def get_predictor() -> ETAPredictorService:
    """Return the centralized singleton ETAPredictorService instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = ETAPredictorService()
    return _predictor_instance


def predict_delay(
    features: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame],
    as_dict: bool = True,
) -> Union[Dict[str, float], List[Dict[str, float]], float, List[float]]:
    """Standalone prediction helper delegating to the centralized ETAPredictorService."""
    return get_predictor().predict_delay(features, as_dict=as_dict)


if __name__ == "__main__":
    predictor = get_predictor()
    result = predictor.verify_model()
    print("Verification result:", json.dumps(result, indent=2))

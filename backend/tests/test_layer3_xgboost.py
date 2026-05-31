import numpy as np
import pytest
from unittest.mock import MagicMock, patch

def make_preprocessing_output(n=10):
    return {
        "status": "OK",
        "scaled_features": np.random.rand(n, 18),
        "nlp_texts": [f"flow {i}" for i in range(n)],
        "ips": [f"10.0.0.{i}" for i in range(n)]
    }

def test_xgboost_returns_predictions():
    with patch('app.layers.xgboost_model.joblib.load') as mock_load:
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0, 1, 2, 0, 1, 2, 3, 4, 0, 1])
        mock_model.predict_proba.return_value = np.random.dirichlet(np.ones(5), size=10)
        mock_load.return_value = mock_model

        from app.layers.xgboost_model import XGBoostLayer
        layer = XGBoostLayer()
        result = layer.run(make_preprocessing_output())

        assert result["status"] == "OK"
        assert len(result["predictions"]) == 10
        assert result["attack_count"] >= 0

def test_xgboost_confidence_valid():
    with patch('app.layers.xgboost_model.joblib.load') as mock_load:
        mock_model = MagicMock()
        mock_model.predict.return_value = np.zeros(5, dtype=int)
        mock_model.predict_proba.return_value = np.random.dirichlet(np.ones(5), size=5)
        mock_load.return_value = mock_model

        from app.layers.xgboost_model import XGBoostLayer
        layer = XGBoostLayer()
        result = layer.run(make_preprocessing_output(5))
        for pred in result["predictions"]:
            assert 0.0 <= pred["confidence"] <= 1.0

def test_xgboost_unknown_label_does_not_crash():
    with patch('app.layers.xgboost_model.joblib.load') as mock_load:
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([12])
        mock_model.predict_proba.return_value = np.array([[0.01, 0.99]])
        mock_load.return_value = mock_model

        from app.layers.xgboost_model import XGBoostLayer
        layer = XGBoostLayer()
        result = layer.run(make_preprocessing_output(1))

        assert result["status"] == "OK"
        assert result["predictions"][0]["attack_type"] == "Class 12"

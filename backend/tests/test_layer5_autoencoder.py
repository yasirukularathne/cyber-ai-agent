import numpy as np
import pytest
from unittest.mock import MagicMock, patch

def make_preprocessing_output(n=10):
    return {"status": "OK", "scaled_features": np.random.rand(n, 18)}

def test_autoencoder_errors_nonnegative():
    with patch('app.layers.autoencoder_model.tf.keras.models.load_model') as mock_ae, \
         patch('app.layers.autoencoder_model.np.load', return_value=np.array([0.05])):
        mock_model = MagicMock()
        mock_model.predict.return_value = np.random.rand(10, 18)
        mock_ae.return_value = mock_model

        from app.layers.autoencoder_model import AutoencoderLayer
        layer = AutoencoderLayer()
        result = layer.run(make_preprocessing_output())

        assert result["status"] == "OK"
        for r in result["results"]:
            assert r["reconstruction_error"] >= 0

def test_high_error_flagged_as_anomaly():
    """Row with very high reconstruction error must be flagged."""
    with patch('app.layers.autoencoder_model.tf.keras.models.load_model') as mock_ae, \
         patch('app.layers.autoencoder_model.np.load', return_value=np.array([0.001])):
        mock_model = MagicMock()
        mock_model.predict.return_value = np.zeros((5, 18))
        mock_ae.return_value = mock_model

        from app.layers.autoencoder_model import AutoencoderLayer
        layer = AutoencoderLayer()
        result = layer.run({"scaled_features": np.ones((5, 18))})
        assert result["anomaly_count"] > 0

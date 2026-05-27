import numpy as np
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

def make_mock_ingestion_output():
    cols = [
        'Flow Duration','Total Fwd Packets','Total Backward Packets',
        'Total Length of Fwd Packets','Total Length of Bwd Packets',
        'Flow Bytes/s','Flow Packets/s','Fwd Packet Length Mean',
        'Bwd Packet Length Mean','Flow IAT Mean','Fwd IAT Mean',
        'Bwd IAT Mean','Fwd PSH Flags','Bwd PSH Flags','Fwd URG Flags',
        'Bwd URG Flags','Destination Port','Average Packet Size'
    ]
    df = pd.DataFrame(np.random.rand(5, len(cols)), columns=cols)
    return {"status": "OK", "dataframe": df, "ips": ["192.168.1.1"]*5}

def test_preprocessing_no_nulls():
    with patch('app.layers.preprocessing.joblib.load'), \
         patch('builtins.open'), \
         patch('json.load', return_value=[]):
        from app.layers.preprocessing import PreprocessingLayer
        layer = PreprocessingLayer.__new__(PreprocessingLayer)
        layer.scaler = MagicMock()
        layer.scaler.transform = lambda x: x.values
        layer.feature_names = []

        result = layer.run(make_mock_ingestion_output())
        assert result["null_count_after_clean"] == 0

def test_nlp_texts_generated():
    with patch('app.layers.preprocessing.joblib.load'), \
         patch('builtins.open'), patch('json.load', return_value=[]):
        from app.layers.preprocessing import PreprocessingLayer
        layer = PreprocessingLayer.__new__(PreprocessingLayer)
        layer.scaler = MagicMock()
        layer.scaler.transform = lambda x: x.values
        layer.feature_names = []

        result = layer.run(make_mock_ingestion_output())
        assert len(result["nlp_texts"]) == 5
        assert "192.168.1.1" in result["nlp_texts"][0]

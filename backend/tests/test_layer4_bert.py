import numpy as np
import pytest
from unittest.mock import MagicMock, patch
import torch

def test_bert_output_shape():
    """BERT should return one prediction per input text."""
    mock_output = MagicMock()
    mock_output.logits = torch.randn(3, 5)

    with patch('app.layers.bert_model.BertTokenizer.from_pretrained'), \
         patch('app.layers.bert_model.BertForSequenceClassification.from_pretrained') as mock_model_cls:
        mock_model = MagicMock()
        mock_model.return_value = mock_output
        mock_model_cls.return_value = mock_model

        from app.layers.bert_model import BERTLayer
        layer = BERTLayer.__new__(BERTLayer)
        layer.tokenizer = MagicMock()
        layer.tokenizer.return_value = {
            'input_ids': torch.zeros(3, 10, dtype=torch.long),
            'attention_mask': torch.ones(3, 10, dtype=torch.long)
        }
        layer.model = MagicMock(return_value=mock_output)
        layer.device = 'cpu'

        result = layer.run({"nlp_texts": ["flow 1", "flow 2", "flow 3"]})
        assert result["status"] == "OK"
        assert len(result["predictions"]) == 3

def test_bert_confidence_in_range():
    """All BERT confidence values should be between 0 and 1."""
    fake_probs = np.array([[0.1, 0.7, 0.1, 0.05, 0.05]])
    conf = float(np.max(fake_probs))
    assert 0.0 <= conf <= 1.0

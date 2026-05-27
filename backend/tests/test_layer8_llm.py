import pytest
from unittest.mock import MagicMock, patch

def make_mcp_output():
    return {
        "status": "OK",
        "enriched_threats": [{
            "ip": "10.0.0.5", "attack_type": "Brute Force",
            "confidence_pct": 91.0, "anomaly_score": 0.09,
            "ae_flagged": True, "severity": "HIGH",
            "ip_reputation": {"reason": "No known threat intelligence"},
            "related_cves": [{"id": "CVE-2023-32784"}],
            "xgb_prediction": "Brute Force",
            "bert_prediction": "Brute Force",
            "incident_summary": "Test"
        }]
    }

def test_llm_returns_explanation():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"explanation":"test","why_dangerous":"test","mitigation":"1. do this","severity":"HIGH","model_agreement":"agree"}'

    with patch('app.layers.llm_explainer.os.getenv', side_effect=lambda k, default=None: 'false' if k == 'USE_GROQ' else 'fake_key'), \
         patch('openai.OpenAI') as MockOpenAI:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        MockOpenAI.return_value = mock_client

        from app.layers.llm_explainer import LLMExplainerLayer
        layer = LLMExplainerLayer()
        result = layer.run(make_mcp_output())

        assert result["status"] == "OK"
        assert len(result["explained_threats"]) == 1
        report = result["explained_threats"][0]["llm_report"]
        assert "explanation" in report
        assert len(report["explanation"]) > 3

from app.layers.fusion import FusionLayer

def make_xgb(n, label=1, conf=0.9):
    return {"predictions": [{"label": label, "attack_type": "Brute Force", "confidence": conf} for _ in range(n)]}

def make_bert(n, label=1, conf=0.85):
    return {"predictions": [{"label": label, "attack_type": "Brute Force", "confidence": conf} for _ in range(n)]}

def make_ae(n, is_anomaly=True, score=1.5, error=0.08):
    return {"results": [{"is_anomaly": is_anomaly, "anomaly_score": score, "reconstruction_error": error} for _ in range(n)]}

def test_fusion_all_agree_attack():
    layer = FusionLayer()
    result = layer.run(make_xgb(3), make_bert(3), make_ae(3), ["1.2.3.4"]*3)
    assert result["status"] == "OK"
    assert result["threat_count"] == 3

def test_fusion_all_agree_benign():
    layer = FusionLayer()
    result = layer.run(make_xgb(3, label=0, conf=0.95),
                       make_bert(3, label=0, conf=0.95),
                       make_ae(3, is_anomaly=False, score=0.1, error=0.001),
                       ["1.2.3.4"]*3)
    assert result["threat_count"] == 0

def test_fused_score_in_range():
    layer = FusionLayer()
    result = layer.run(make_xgb(5), make_bert(5), make_ae(5), ["x"]*5)
    for r in result["all_results"]:
        assert 0.0 <= r["fused_score"] <= 1.5  # score can exceed 1 on anomaly

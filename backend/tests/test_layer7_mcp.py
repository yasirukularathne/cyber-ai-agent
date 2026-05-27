from app.layers.mcp_tools import MCPToolLayer

def make_fusion_output(ip="45.12.22.1", attack="Brute Force", severity="HIGH"):
    return {
        "status": "OK",
        "threats": [{
            "ip": ip, "attack_type": attack, "attack_label": 1,
            "fused_score": 0.88, "confidence_pct": 88.0,
            "severity": severity, "is_threat": True,
            "xgb_prediction": attack, "bert_prediction": attack,
            "ae_flagged": True, "anomaly_score": 0.07
        }],
        "threat_count": 1
    }

def test_known_ip_flagged():
    layer = MCPToolLayer()
    result = layer.run(make_fusion_output(ip="45.12.22.1"))
    assert result["known_bad_ips"] == 1
    assert result["enriched_threats"][0]["ip_is_known_bad"] is True

def test_cves_populated():
    layer = MCPToolLayer()
    result = layer.run(make_fusion_output(attack="Brute Force"))
    cves = result["enriched_threats"][0]["related_cves"]
    assert len(cves) > 0
    assert "id" in cves[0]

def test_incident_summary_not_empty():
    layer = MCPToolLayer()
    result = layer.run(make_fusion_output())
    summary = result["enriched_threats"][0]["incident_summary"]
    assert len(summary) > 20

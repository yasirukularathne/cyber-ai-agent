from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ThreatResult(BaseModel):
    ip: str
    attack_type: str
    attack_label: int
    fused_score: float
    confidence_pct: float
    severity: str
    is_threat: bool
    xgb_prediction: str
    bert_prediction: str
    ae_flagged: bool
    anomaly_score: float
    timestamp: Optional[str] = None

class EnrichedThreat(ThreatResult):
    ip_reputation: Dict[str, Any]
    related_cves: List[Dict[str, str]]
    ip_is_known_bad: bool
    incident_summary: str

class LLMReport(EnrichedThreat):
    llm_report: Dict[str, str]

class PipelineResponse(BaseModel):
    run_id: str
    total_records: int
    threats_detected: int
    summary: str
    threats: List[Dict]
    enriched_threats: List[Dict]
    explained_threats: List[Dict]
    debug: Optional[Dict] = None

from fastapi import APIRouter
from app.routes.predict import get_last_result

router = APIRouter()

@router.get('/dashboard')
def get_dashboard():
    result = get_last_result()
    threats = result.get('threats', [])

    severity_counts = {}
    attack_counts = {}
    for t in threats:
        sev = t.get('severity', 'UNKNOWN')
        atk = t.get('attack_type', 'Unknown')
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        attack_counts[atk]   = attack_counts.get(atk, 0) + 1

    return {
        'total_records':   result.get('total_records', 0),
        'threat_count':    result.get('threats_detected', 0),
        'severity_counts': severity_counts,
        'attack_counts':   attack_counts,
        'recent_threats':  threats[:10],
        'run_id':          result.get('run_id', None)
    }

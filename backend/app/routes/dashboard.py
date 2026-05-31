from fastapi import APIRouter
from app.routes.predict import get_last_result

router = APIRouter()


def _summarize_classifier(predictions: list, ips: list) -> dict:
    total = len(predictions)
    detections = [item for item in predictions if item.get('label') != 0]
    top_detections = []

    for item in detections[:5]:
        index = item.get('index', 0)
        top_detections.append({
            'index': index,
            'ip': ips[index] if index < len(ips) else 'unknown',
            'label': item.get('label'),
            'attack_type': item.get('attack_type', f"Class {item.get('label')}"),
            'confidence': item.get('confidence', 0),
        })

    return {
        'total': total,
        'detected': len(detections),
        'benign': max(total - len(detections), 0),
        'top_detections': top_detections,
    }


def _summarize_autoencoder(results: list, ips: list) -> dict:
    total = len(results)
    anomalies = [item for item in results if item.get('is_anomaly')]
    top_anomalies = []

    for item in anomalies[:5]:
        index = item.get('index', 0)
        top_anomalies.append({
            'index': index,
            'ip': ips[index] if index < len(ips) else 'unknown',
            'is_anomaly': item.get('is_anomaly', False),
            'anomaly_score': item.get('anomaly_score', 0),
            'reconstruction_error': item.get('reconstruction_error', 0),
        })

    return {
        'total': total,
        'detected': len(anomalies),
        'benign': max(total - len(anomalies), 0),
        'top_detections': top_anomalies,
    }

@router.get('/dashboard')
def get_dashboard():
    result = get_last_result()
    threats = result.get('threats', [])
    debug = result.get('debug', {}) if isinstance(result.get('debug', {}), dict) else {}
    ips = debug.get('ingestion', {}).get('ips', []) if isinstance(debug.get('ingestion', {}), dict) else []

    severity_counts = {}
    attack_counts = {}
    for t in threats:
        sev = t.get('severity', 'UNKNOWN')
        atk = t.get('attack_type', 'Unknown')
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        attack_counts[atk]   = attack_counts.get(atk, 0) + 1

    model_breakdown = {}
    if isinstance(debug, dict):
        model_breakdown = {
            'xgboost': _summarize_classifier(debug.get('xgboost', {}).get('predictions', []), ips),
            'bert': _summarize_classifier(debug.get('bert', {}).get('predictions', []), ips),
            'autoencoder': _summarize_autoencoder(debug.get('autoencoder', {}).get('results', []), ips),
        }

    return {
        'total_records':   result.get('total_records', 0),
        'threat_count':    result.get('threats_detected', 0),
        'severity_counts': severity_counts,
        'attack_counts':   attack_counts,
        'recent_threats':  threats[:10],
        'model_breakdown': model_breakdown,
        'run_id':          result.get('run_id', None)
    }

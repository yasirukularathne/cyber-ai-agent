from app.utils.logger import get_logger

logger = get_logger('fusion')

ATTACK_LABELS = {0: 'Benign', 1: 'Brute Force', 2: 'DDoS/DoS', 3: 'Port Scan', 4: 'Botnet'}
SEVERITY_MAP  = {0: 'NONE', 1: 'HIGH', 2: 'CRITICAL', 3: 'MEDIUM', 4: 'HIGH'}
WEIGHTS = {'xgboost': 0.40, 'bert': 0.40, 'autoencoder': 0.20}

class FusionLayer:
    """
    Layer 6: Weighted ensemble.
    XGBoost 40% + BERT 40% + Autoencoder 20%.
    Final label chosen by highest-confidence supervised model when they disagree.
    """

    def run(self, xgb_out: dict, bert_out: dict, ae_out: dict, ips: list) -> dict:
        try:
            xgb_preds  = xgb_out['predictions']
            bert_preds = bert_out['predictions']
            ae_results = ae_out['results']
            n = min(len(xgb_preds), len(bert_preds), len(ae_results))
            logger.info(f'Fusion running on {n} rows')

            fused = []
            for i in range(n):
                xgb_label  = xgb_preds[i]['label']
                bert_label = bert_preds[i]['label']
                xgb_conf   = xgb_preds[i]['confidence']
                bert_conf  = bert_preds[i]['confidence']
                ae_anomaly = ae_results[i]['is_anomaly']
                ae_score   = ae_results[i]['anomaly_score']

                xgb_attack  = int(xgb_label != 0)
                bert_attack = int(bert_label != 0)
                ae_attack   = int(ae_anomaly)

                combined = (
                    WEIGHTS['xgboost']     * xgb_conf  * xgb_attack +
                    WEIGHTS['bert']        * bert_conf  * bert_attack +
                    WEIGHTS['autoencoder'] * min(ae_score, 1.0) * ae_attack
                )

                if xgb_label == bert_label:
                    final_label = xgb_label
                elif xgb_conf >= bert_conf:
                    final_label = xgb_label
                else:
                    final_label = bert_label

                if combined < 0.15:
                    final_label = 0

                fused.append({
                    'index': i,
                    'ip': ips[i] if i < len(ips) else 'unknown',
                    'attack_type': ATTACK_LABELS[final_label],
                    'attack_label': final_label,
                    'fused_score': round(combined, 4),
                    'confidence_pct': round(combined * 100, 2),
                    'severity': SEVERITY_MAP[final_label],
                    'is_threat': final_label != 0,
                    'xgb_prediction': xgb_preds[i]['attack_type'],
                    'bert_prediction': bert_preds[i]['attack_type'],
                    'ae_flagged': ae_anomaly,
                    'anomaly_score': ae_results[i]['reconstruction_error']
                })

            threats = [f for f in fused if f['is_threat']]
            logger.info(f'Fusion: {len(threats)} threats identified')

            return {
                'status': 'OK',
                'layer': 'fusion',
                'total': n,
                'threats': threats,
                'threat_count': len(threats),
                'all_results': fused
            }
        except Exception as e:
            logger.error(f'Fusion failed: {e}')
            return {'status': 'ERROR', 'layer': 'fusion', 'error': str(e)}

from app.utils.logger import get_logger
from app.layers.label_map import ATTACK_LABELS

logger = get_logger('fusion')

SEVERITY_MAP = {0: 'NONE', 1: 'HIGH', 2: 'CRITICAL', 3: 'MEDIUM', 4: 'HIGH'}
WEIGHTS = {'xgboost': 0.40, 'bert': 0.40, 'autoencoder': 0.20}

# Default severity for an anomaly that ONLY the autoencoder flagged —
# neither supervised model assigned a specific attack class, so we stay
# cautious rather than escalating straight to HIGH/CRITICAL.
UNCLASSIFIED_ANOMALY_SEVERITY = 'MEDIUM'


class FusionLayer:
    """
    Layer 6: Ensemble fusion across XGBoost, BERT, and the autoencoder.

    Threat decision: OR across all three detectors — if ANY model flags
    attack/anomaly, the row is treated as a threat. (Previously, an
    absolute combined-score cutoff could override and erase a threat
    even when XGBoost and BERT agreed on it — see fix below.)

    Label/severity resolution: when XGBoost and BERT disagree on the
    specific attack class, the higher-confidence model's label wins.
    The weighted `combined` score is now used only for reporting
    (confidence_pct / relative severity), not as a veto.
    """

    def run(self, xgb_out: dict, bert_out: dict, ae_out: dict, ips: list) -> dict:
        try:
            xgb_preds  = xgb_out['predictions']
            bert_preds = bert_out['predictions']
            ae_results = ae_out['results']

            lengths = {'xgboost': len(xgb_preds), 'bert': len(bert_preds), 'autoencoder': len(ae_results)}
            n = min(lengths.values())
            if len(set(lengths.values())) > 1:
                # FIX: previously this mismatch was silently truncated with
                # no record of it — log it so misaligned upstream outputs
                # don't go unnoticed.
                logger.warning(f'Fusion: input length mismatch {lengths}, truncating to {n}')

            logger.info(f'Fusion running on {n} rows')
            fused = []

            for i in range(n):
                xgb_label  = xgb_preds[i]['label']
                bert_label = bert_preds[i]['label']
                xgb_conf   = xgb_preds[i]['confidence']
                bert_conf  = bert_preds[i]['confidence']
                ae_anomaly = ae_results[i]['is_anomaly']
                ae_score   = ae_results[i]['anomaly_score']
                ae_recon_error = ae_results[i]['reconstruction_error']

                xgb_attack  = int(xgb_label != 0)
                bert_attack = int(bert_label != 0)
                ae_attack   = int(ae_anomaly)

                combined = (
                    WEIGHTS['xgboost']     * xgb_conf * xgb_attack +
                    WEIGHTS['bert']        * bert_conf * bert_attack +
                    WEIGHTS['autoencoder'] * min(ae_score, 1.0) * ae_attack
                )

                # ── Resolve a multiclass label, preferring the more
                # confident supervised model when they disagree.
                if xgb_label == bert_label:
                    resolved_label = xgb_label
                elif xgb_conf >= bert_conf:
                    resolved_label = xgb_label
                else:
                    resolved_label = bert_label

                # ── FIX: threat decision is OR across all three detectors,
                # no longer vetoed by an absolute combined-score cutoff.
                is_threat = bool(xgb_attack) or bool(bert_attack) or bool(ae_attack)

                if not is_threat:
                    final_label = 0
                elif resolved_label != 0:
                    # At least one supervised model named a specific class.
                    final_label = resolved_label
                elif xgb_attack:
                    final_label = xgb_label
                elif bert_attack:
                    final_label = bert_label
                else:
                    # Only the autoencoder flagged this row — no classifier
                    # assigned a specific attack type.
                    final_label = None

                if final_label is None:
                    final_attack_type = 'Unclassified Anomaly (Autoencoder Only)'
                    final_severity = UNCLASSIFIED_ANOMALY_SEVERITY
                    attack_label_out = -1
                else:
                    final_attack_type = ATTACK_LABELS.get(final_label, f'Class {final_label}')
                    final_severity = SEVERITY_MAP.get(final_label, 'HIGH' if final_label != 0 else 'NONE')
                    attack_label_out = final_label

                fused.append({
                    'index': i,
                    'ip': ips[i] if i < len(ips) else 'unknown',
                    'attack_type': final_attack_type,
                    'attack_label': attack_label_out,
                    'fused_score': round(combined, 4),
                    'confidence_pct': round(combined * 100, 2),
                    'severity': final_severity,
                    'is_threat': is_threat,
                    'xgb_prediction': xgb_preds[i]['attack_type'],
                    'bert_prediction': bert_preds[i]['attack_type'],
                    'ae_flagged': ae_anomaly,
                    'anomaly_score': ae_score,            # FIX: the score actually used in fusion
                    'reconstruction_error': ae_recon_error  # FIX: raw AE error, kept separately
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
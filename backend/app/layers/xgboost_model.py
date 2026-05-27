import numpy as np
import joblib
from app.utils.logger import get_logger

logger = get_logger('xgboost')

ATTACK_LABELS = {0: 'Benign', 1: 'Brute Force', 2: 'DDoS/DoS', 3: 'Port Scan', 4: 'Botnet'}

class XGBoostLayer:
    """
    Layer 3: Supervised attack classification using XGBoost.
    Returns per-row attack type and confidence.
    """

    def __init__(self):
        self.model = joblib.load('trained_models/xgboost_model.pkl')
        logger.info('XGBoost model loaded.')

    def run(self, preprocessing_output: dict) -> dict:
        try:
            features = preprocessing_output['scaled_features']
            logger.info(f'XGBoost predicting on {len(features)} rows')

            predictions  = self.model.predict(features)
            probabilities = self.model.predict_proba(features)

            results = []
            for i in range(len(features)):
                label = int(predictions[i])
                conf  = float(np.max(probabilities[i]))
                results.append({
                    'index': i,
                    'label': label,
                    'attack_type': ATTACK_LABELS[label],
                    'confidence': round(conf, 4),
                    'all_probs': probabilities[i].tolist()
                })

            attack_count = sum(1 for r in results if r['label'] != 0)
            logger.info(f'XGBoost: {attack_count} attacks detected')

            return {
                'status': 'OK',
                'layer': 'xgboost',
                'predictions': results,
                'attack_count': attack_count
            }
        except Exception as e:
            logger.error(f'XGBoost failed: {e}')
            return {'status': 'ERROR', 'layer': 'xgboost', 'error': str(e)}

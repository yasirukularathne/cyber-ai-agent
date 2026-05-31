import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from app.utils.logger import get_logger
from app.layers.label_map import ATTACK_LABELS

logger = get_logger('xgboost')
BASE_DIR = Path(__file__).resolve().parents[2]

class XGBoostLayer:
    """
    Layer 3: Supervised attack classification using XGBoost.
    Returns per-row attack type and confidence.
    """

    def __init__(self):
        self.model = joblib.load(BASE_DIR / 'trained_models' / 'xgboost_model.pkl')
        logger.info('XGBoost model loaded.')

    def _prepare_features(self, preprocessing_output: dict):
        features = preprocessing_output['scaled_features']
        expected_columns = getattr(self.model, 'feature_names_in_', None)

        if not isinstance(expected_columns, (list, tuple, np.ndarray, pd.Index)):
            expected_columns = None
        elif len(expected_columns) == 0:
            expected_columns = None

        if expected_columns is None:
            raw_features = preprocessing_output.get('raw_features')
            if isinstance(raw_features, pd.DataFrame) and len(raw_features.columns) > 0:
                expected_columns = raw_features.columns

        if isinstance(features, pd.DataFrame):
            if expected_columns is not None:
                return features.reindex(columns=list(expected_columns), fill_value=0)
            return features

        if expected_columns is not None:
            return pd.DataFrame(features, columns=list(expected_columns))

        return features

    def run(self, preprocessing_output: dict) -> dict:
        try:
            features = self._prepare_features(preprocessing_output)
            logger.info(f'XGBoost predicting on {len(features)} rows')

            predictions = self.model.predict(features)
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features)
            else:
                probabilities = np.asarray(predictions)

            results = []
            for i in range(len(features)):
                label = int(predictions[i])
                if np.ndim(probabilities) > 1:
                    confidence = float(np.max(probabilities[i]))
                    all_probs = probabilities[i].tolist()
                else:
                    confidence = 1.0
                    all_probs = [float(probabilities[i])]
                results.append({
                    'index': i,
                    'label': label,
                    'attack_type': ATTACK_LABELS.get(label, f'Class {label}'),
                    'confidence': round(confidence, 4),
                    'all_probs': all_probs
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

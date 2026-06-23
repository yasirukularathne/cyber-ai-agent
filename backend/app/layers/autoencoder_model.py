import json
import numpy as np
import tensorflow as tf
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger('autoencoder')
BASE_DIR = Path(__file__).resolve().parents[2]


class AutoencoderLayer:
    """
    Layer 5: Unsupervised anomaly detection.
    Trained only on benign traffic. High reconstruction error = anomaly.
    """

    def __init__(self):
        self.model = tf.keras.models.load_model(
            BASE_DIR / 'trained_models' / 'autoencoder.keras'
        )

        # FIX: load the threshold from the SAME file the training notebook
        # actually writes (autoencoder_threshold.json), not the unrelated
        # ae_threshold.npy, which is never produced by current training
        # and has no guaranteed relationship to the loaded model's weights.
        threshold_path = BASE_DIR / 'trained_models' / 'autoencoder_threshold.json'
        with open(threshold_path, 'r') as f:
            threshold_data = json.load(f)

        self.threshold = float(threshold_data['threshold'])
        logger.info(
            f'Autoencoder loaded. Threshold: {self.threshold:.6f} '
            f'({threshold_data.get("threshold_name", "unknown")})'
        )

    def run(self, preprocessing_output: dict) -> dict:
        try:
            features = preprocessing_output['scaled_features']
            logger.info(f'Autoencoder running on {len(features)} rows')

            reconstructed = self.model.predict(features, verbose=0)
            errors = np.mean((features - reconstructed) ** 2, axis=1)

            results = []
            for i, error in enumerate(errors):
                is_anomaly = bool(error > self.threshold)
                results.append({
                    'index': i,
                    'reconstruction_error': round(float(error), 6),
                    'is_anomaly': is_anomaly,
                    'anomaly_score': round(float(error / self.threshold), 4)
                })

            anomaly_count = sum(1 for r in results if r['is_anomaly'])
            logger.info(f'Autoencoder: {anomaly_count} anomalies detected')

            return {
                'status': 'OK',
                'layer': 'autoencoder',
                'threshold': self.threshold,
                'anomaly_count': anomaly_count,
                'results': results,
                'mean_error': round(float(np.mean(errors)), 6),
                'max_error': round(float(np.max(errors)), 6)
            }
        except Exception as e:
            logger.error(f'Autoencoder failed: {e}')
            return {'status': 'ERROR', 'layer': 'autoencoder', 'error': str(e)}
import numpy as np
import tensorflow as tf
from app.utils.logger import get_logger

logger = get_logger('autoencoder')

class AutoencoderLayer:
    """
    Layer 5: Unsupervised anomaly detection.
    Trained only on benign traffic. High reconstruction error = anomaly.
    """

    def __init__(self):
        self.model = tf.keras.models.load_model('trained_models/autoencoder.keras')
        self.threshold = float(np.load('trained_models/ae_threshold.npy')[0])
        logger.info(f'Autoencoder loaded. Threshold: {self.threshold:.6f}')

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

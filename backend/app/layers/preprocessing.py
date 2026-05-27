import pandas as pd
import numpy as np
import joblib
import json

FEATURES = [
    'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
    'Flow Bytes/s', 'Flow Packets/s', 'Fwd Packet Length Mean',
    'Bwd Packet Length Mean', 'Flow IAT Mean', 'Fwd IAT Mean',
    'Bwd IAT Mean', 'Fwd PSH Flags', 'Bwd PSH Flags',
    'Fwd URG Flags', 'Bwd URG Flags', 'Destination Port',
    'Average Packet Size'
]

class PreprocessingLayer:
    """
    Layer 2: Cleans raw DataFrame, scales features, and generates
    NLP text representations for BERT input.
    """

    def __init__(self):
        self.scaler = joblib.load('trained_models/scaler.pkl')
        with open('trained_models/feature_names.json') as f:
            self.feature_names = json.load(f)

    def run(self, ingestion_output: dict) -> dict:
        try:
            df = ingestion_output['dataframe'].copy()
            ips = ingestion_output['ips']

            df_features = df[FEATURES].copy()
            df_features.replace([np.inf, -np.inf], np.nan, inplace=True)
            df_features.fillna(0, inplace=True)

            null_count = int(df_features.isnull().sum().sum())
            scaled = self.scaler.transform(df_features)
            nlp_texts = self._to_nlp_text(df_features, ips)

            return {
                'status': 'OK',
                'layer': 'preprocessing',
                'row_count': len(scaled),
                'null_count_after_clean': null_count,
                'scaled_features': scaled,
                'raw_features': df_features,
                'nlp_texts': nlp_texts,
                'ips': ips
            }
        except Exception as e:
            return {'status': 'ERROR', 'layer': 'preprocessing', 'error': str(e)}

    def _to_nlp_text(self, df: pd.DataFrame, ips: list) -> list:
        texts = []
        for i, (_, row) in enumerate(df.iterrows()):
            ip = ips[i] if i < len(ips) else 'unknown'
            text = (
                f"Network flow from IP {ip}. "
                f"Duration {row.get('Flow Duration', 0):.1f}ms. "
                f"Forward packets: {row.get('Total Fwd Packets', 0):.0f}. "
                f"Backward packets: {row.get('Total Backward Packets', 0):.0f}. "
                f"Flow rate: {row.get('Flow Bytes/s', 0):.2f} bytes/s. "
                f"Destination port: {row.get('Destination Port', 0):.0f}."
            )
            texts.append(text)
        return texts

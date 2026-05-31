import pandas as pd
import numpy as np
import joblib
import json
import pickle

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

    def __init__(self):
        self.scaler = joblib.load('trained_models/scaler.pkl')
        self.feature_names = self._load_feature_names('trained_models/feature_names.json')

    # ─────────────────────────────────────────────────────────────
    def _expected_feature_order(self):
        scaler_features = getattr(self.scaler, 'feature_names_in_', None)

        if scaler_features is not None:
            return list(map(str, scaler_features))

        if self.feature_names:
            return list(map(str, self.feature_names))

        return FEATURES

    # ─────────────────────────────────────────────────────────────
    def _load_feature_names(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            try:
                with open(path, 'rb') as f:
                    return pickle.load(f)
            except:
                return []

    # ─────────────────────────────────────────────────────────────
    def run(self, ingestion_output: dict) -> dict:
        try:
            df = ingestion_output['dataframe'].copy()
            ips = ingestion_output.get('ips', [])

            # ── Feature alignment ────────────────────────────────
            expected_features = self._expected_feature_order()
            df = df.reindex(columns=expected_features, fill_value=0)

            # ── Clean data ───────────────────────────────────────
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df.fillna(0, inplace=True)

            # ── Scale ────────────────────────────────────────────
            scaled = self.scaler.transform(df)

            # ── NLP generation (IMPORTANT FIX) ───────────────────
            nlp_texts = self._to_nlp_text(df, ips)

            return {
                "status": "OK",
                "layer": "preprocessing",
                "row_count": len(df),
                "scaled_features": scaled,
                "raw_features": df,
                "nlp_texts": nlp_texts,
                "ips": ips
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "layer": "preprocessing",
                "error": str(e)
            }

    # ─────────────────────────────────────────────────────────────
    def _to_nlp_text(self, df: pd.DataFrame, ips: list):

        texts = []

        for i, (_, row) in enumerate(df.iterrows()):
            ip = ips[i] if i < len(ips) else "unknown"

            # ── derived features (MATCH TRAINING STYLE) ─────────
            fwd_pkts = row.get('Total Fwd Packets', 0)
            bwd_pkts = row.get('Total Backward Packets', 0)
            avg_pkt = row.get('Average Packet Size', 0)
            flow_pps = row.get('Flow Packets/s', 0)

            pkt_ratio = fwd_pkts / max(bwd_pkts, 1)

            # ── semantic labels (MATCH TRAINING GENERATOR) ─────
            if flow_pps > 1000:
                traffic = "high traffic burst pattern"
            elif flow_pps > 300:
                traffic = "moderate network activity"
            else:
                traffic = "normal network flow"

            payload = "large payload" if avg_pkt > 800 else "small payload"
            flow_balance = "skewed traffic flow" if pkt_ratio > 2 or pkt_ratio < 0.5 else "balanced traffic flow"

            # ── FINAL TEXT (MATCH TRAINING FORMAT) ──────────────
            text = (
                f"Network flow detected from IP {ip}. "
                f"Duration {row.get('Flow Duration', 0):.1f} ms with "
                f"{int(fwd_pkts + bwd_pkts)} packets observed. "
                f"Forward packets {int(fwd_pkts)}, backward packets {int(bwd_pkts)}. "
                f"Traffic rate {row.get('Flow Bytes/s', 0):.2f} bytes per second. "
                f"Packet size indicates {payload}. "
                f"Flow behavior shows {flow_balance}. "
                f"Overall pattern indicates {traffic}."
            )

            texts.append(" ".join(text.split()))

        return texts
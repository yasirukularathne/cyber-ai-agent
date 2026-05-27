import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime

REQUIRED_COLUMNS = [
    'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
    'Flow Bytes/s', 'Flow Packets/s', 'Fwd Packet Length Mean',
    'Bwd Packet Length Mean', 'Flow IAT Mean', 'Fwd IAT Mean',
    'Bwd IAT Mean', 'Fwd PSH Flags', 'Bwd PSH Flags',
    'Fwd URG Flags', 'Bwd URG Flags', 'Destination Port',
    'Average Packet Size'
]

class IngestionLayer:
    """
    Layer 1: Accepts raw CSV string, returns a structured DataFrame.
    Extracts metadata: IP addresses, row count, column list.
    """

    def run(self, file_content: str) -> dict:
        try:
            df = pd.read_csv(StringIO(file_content))
            df.columns = df.columns.str.strip()

            ips = self._extract_ips(df)

            missing = set(REQUIRED_COLUMNS) - set(df.columns)
            if missing:
                return {
                    'status': 'ERROR',
                    'error': f'Missing columns: {missing}',
                    'layer': 'ingestion'
                }

            return {
                'status': 'OK',
                'layer': 'ingestion',
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
                'ips': ips,
                'dataframe': df,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'ERROR', 'layer': 'ingestion', 'error': str(e)}

    def _extract_ips(self, df: pd.DataFrame) -> list:
        for col in ['Source IP', 'Src IP', 'src_ip', 'Source_IP', 'src']:
            if col in df.columns:
                return df[col].tolist()
        return [f'192.168.1.{(i % 254) + 1}' for i in range(len(df))]

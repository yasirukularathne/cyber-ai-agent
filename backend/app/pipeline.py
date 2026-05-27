import json
import os
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger('pipeline')

# Singletons - loaded once at startup
_ingestion = None
_preprocessing = None
_xgboost = None
_bert = None
_autoencoder = None
_fusion = None
_mcp = None
_llm = None

def _load_models():
    global _ingestion, _preprocessing, _xgboost, _bert, _autoencoder, _fusion, _mcp, _llm
    if _ingestion is not None:
        return
    logger.info('Loading all models...')
    from app.layers.ingestion         import IngestionLayer
    from app.layers.preprocessing     import PreprocessingLayer
    from app.layers.xgboost_model     import XGBoostLayer
    from app.layers.bert_model        import BERTLayer
    from app.layers.autoencoder_model import AutoencoderLayer
    from app.layers.fusion            import FusionLayer
    from app.layers.mcp_tools         import MCPToolLayer
    from app.layers.llm_explainer     import LLMExplainerLayer

    _ingestion     = IngestionLayer()
    _preprocessing = PreprocessingLayer()
    _xgboost       = XGBoostLayer()
    _bert          = BERTLayer()
    _autoencoder   = AutoencoderLayer()
    _fusion        = FusionLayer()
    _mcp           = MCPToolLayer()
    _llm           = LLMExplainerLayer()
    logger.info('All models loaded successfully.')

def run_pipeline(file_content: str, debug: bool = False) -> dict:
    _load_models()
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    pipeline_log = {'run_id': run_id, 'layers': {}}

    def record(name: str, output: dict):
        if output['status'] == 'ERROR':
            raise RuntimeError(f'[{name}] Layer failed: {output["error"]}')
        pipeline_log['layers'][name] = _safe_serialize(output)
        logger.info(f'Layer [{name}] OK')
        return output

    L1 = record('ingestion',     _ingestion.run(file_content))
    L2 = record('preprocessing', _preprocessing.run(L1))
    L3 = record('xgboost',       _xgboost.run(L2))
    L4 = record('bert',          _bert.run(L2))
    L5 = record('autoencoder',   _autoencoder.run(L2))
    L6 = record('fusion',        _fusion.run(L3, L4, L5, L2['ips']))
    L7 = record('mcp',           _mcp.run(L6))
    L8 = record('llm',           _llm.run(L7))

    _save_debug_log(run_id, pipeline_log)

    final = {
        'run_id':             run_id,
        'total_records':      L1['row_count'],
        'threats_detected':   L6['threat_count'],
        'threats':            L6['threats'],
        'enriched_threats':   L7['enriched_threats'],
        'explained_threats':  L8['explained_threats'],
        'summary': f"Analyzed {L1['row_count']} records. {L6['threat_count']} threats found."
    }

    if debug:
        final['debug'] = pipeline_log['layers']

    return final

def _safe_serialize(obj):
    import numpy as np
    import pandas as pd
    if isinstance(obj, dict):
        return {k: _safe_serialize(v) for k, v in obj.items()
                if k not in ('dataframe', 'scaled_features', 'raw_features')}
    if isinstance(obj, list):
        return [_safe_serialize(i) for i in obj[:50]]  # cap lists at 50
    if isinstance(obj, (np.integer,)):  return int(obj)
    if isinstance(obj, (np.floating,)): return float(obj)
    if isinstance(obj, np.ndarray):     return f'<ndarray shape={obj.shape}>'
    if isinstance(obj, pd.DataFrame):   return f'<DataFrame shape={obj.shape}>'
    return obj

def _save_debug_log(run_id: str, log: dict):
    os.makedirs('debug_logs', exist_ok=True)
    path = f'debug_logs/run_{run_id}.json'
    with open(path, 'w') as f:
        json.dump(log, f, indent=2, default=str)
    logger.info(f'Debug log saved: {path}')

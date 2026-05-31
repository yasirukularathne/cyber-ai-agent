from fastapi import APIRouter
import os, json

router = APIRouter()

@router.get('/debug/runs')
def list_debug_runs():
    if not os.path.exists('debug_logs'):
        return {'runs': []}
    files = sorted(
        [f for f in os.listdir('debug_logs') if f.endswith('.json')],
        reverse=True
    )
    return {'runs': [f.replace('run_','').replace('.json','') for f in files]}

@router.get('/debug/run/{run_id}')
def get_debug_run(run_id: str):
    path = f'debug_logs/run_{run_id}.json'
    if not os.path.exists(path):
        return {'error': 'Run not found', 'run_id': run_id}
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {'error': 'Debug file is not valid JSON', 'run_id': run_id}

@router.get('/debug/latest')
def get_debug_latest():
    if not os.path.exists('debug_logs'):
        return {'error': 'No debug runs yet. Run /api/predict first.'}
    files = sorted(
        [f for f in os.listdir('debug_logs') if f.endswith('.json')],
        reverse=True
    )
    if not files:
        return {'error': 'No runs found.'}
    try:
        with open(f'debug_logs/{files[0]}') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {'error': 'Latest debug file is not valid JSON', 'filename': files[0]}

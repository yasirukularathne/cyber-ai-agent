from fastapi import APIRouter
from app.routes.predict import get_last_result

router = APIRouter()

@router.get('/reports')
def get_reports():
    result = get_last_result()
    explained = result.get('explained_threats', [])
    return {
        'count': len(explained),
        'reports': explained
    }

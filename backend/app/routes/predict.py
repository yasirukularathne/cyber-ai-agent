from fastapi import APIRouter, HTTPException, Query
from app.routes.upload import get_uploaded_content
from app.pipeline import run_pipeline

router = APIRouter()
_last_result = {}

@router.post('/predict')
async def predict(filename: str, debug: bool = Query(False)):
    content = get_uploaded_content()
    if filename not in content:
        raise HTTPException(status_code=404, detail='File not found. Upload first using /api/upload-logs.')
    try:
        result = run_pipeline(content[filename], debug=debug)
        _last_result.clear()
        _last_result.update(result)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Pipeline error: {str(e)}')

def get_last_result():
    return _last_result

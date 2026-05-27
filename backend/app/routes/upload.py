from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()
_uploaded_content = {}

@router.post('/upload-logs')
async def upload_logs(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='Only CSV files are accepted.')
    content = await file.read()
    try:
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        content_str = content.decode('latin-1') # Fallback if utf-8 fails
    _uploaded_content[file.filename] = content_str
    return {
        'filename': file.filename,
        'status': 'uploaded',
        'size_bytes': len(content),
        'message': 'File ready for analysis. Call /api/predict next.'
    }

def get_uploaded_content():
    return _uploaded_content

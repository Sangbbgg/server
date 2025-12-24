from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import aiofiles
from app.core.database import get_db
from app.core.config import settings
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("/")
async def upload_zip(
    file: UploadFile = File(...),
    worker: str = None,
    db: Session = Depends(get_db)
):
    """
    ZIP 파일 업로드 및 처리
    """
    # 파일 크기 검증
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit")
    
    # ZIP 파일인지 확인
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")
    
    # 업로드 디렉토리 생성
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 파일 저장
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    try:
        # 업로드 서비스로 처리
        service = UploadService(db)
        stats = service.process_upload(file_path, worker)
        
        return {
            "message": "Upload processed successfully",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        # 원본 ZIP 파일 삭제 (선택사항)
        if os.path.exists(file_path):
            os.remove(file_path)


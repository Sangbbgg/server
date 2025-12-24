from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models import MaintenanceLog, Asset
from pydantic import BaseModel

router = APIRouter()


class MaintenanceLogResponse(BaseModel):
    id: int
    asset_id: int
    check_date: date
    check_type: str
    worker: Optional[str]
    result_status: str
    
    class Config:
        from_attributes = True


@router.get("/logs", response_model=List[MaintenanceLogResponse])
def get_maintenance_logs(
    asset_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """점검 이력 조회"""
    query = db.query(MaintenanceLog)
    
    if asset_id:
        query = query.filter(MaintenanceLog.asset_id == asset_id)
    if start_date:
        query = query.filter(MaintenanceLog.check_date >= start_date)
    if end_date:
        query = query.filter(MaintenanceLog.check_date <= end_date)
    
    return query.order_by(MaintenanceLog.check_date.desc()).all()


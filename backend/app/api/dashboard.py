from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from typing import Dict, List
from app.core.database import get_db
from app.models import Asset, MaintenanceLog, MaintenanceDetail
from app.models.maintenance import ResultStatus

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """대시보드 통계 정보"""
    # 전체 자산 수
    total_assets = db.query(func.count(Asset.id)).scalar()
    
    # 운영 중인 자산 수
    from app.models.asset import AssetStatus
    operational_assets = db.query(func.count(Asset.id)).filter(
        Asset.status == AssetStatus.OPERATIONAL
    ).scalar()
    
    # 최근 24시간 내 업로드된 로그
    yesterday = date.today() - timedelta(days=1)
    recent_logs = db.query(func.count(MaintenanceLog.id)).filter(
        MaintenanceLog.check_date >= yesterday
    ).scalar()
    
    # Level 1 이벤트가 있는 자산 (경고)
    warning_assets = db.query(Asset).join(MaintenanceLog).join(MaintenanceDetail).filter(
        and_(
            MaintenanceLog.check_date >= yesterday,
            MaintenanceLog.result_status == ResultStatus.FAIL,
            MaintenanceDetail.item_name.like('%Event Stats%')
        )
    ).distinct().all()
    
    return {
        "total_assets": total_assets,
        "operational_assets": operational_assets,
        "recent_logs": recent_logs,
        "warning_assets": [{"id": a.id, "name": a.name} for a in warning_assets]
    }


@router.get("/tree")
def get_system_tree(db: Session = Depends(get_db)):
    """설비 계층 트리 구조"""
    from app.models import System
    
    def build_tree(parent_id=None):
        systems = db.query(System).filter(System.parent_id == parent_id).all()
        result = []
        for system in systems:
            result.append({
                "id": system.id,
                "name": system.name,
                "description": system.description,
                "children": build_tree(system.id)
            })
        return result
    
    return {"tree": build_tree()}


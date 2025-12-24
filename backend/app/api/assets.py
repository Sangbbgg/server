from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.core.database import get_db
from app.models import Asset, NetworkInterface, Account
from pydantic import BaseModel

router = APIRouter()


class AssetResponse(BaseModel):
    id: int
    name: str
    asset_tag: Optional[str]
    system_id: Optional[int]
    location_id: Optional[int]
    status: str
    model: Optional[str]
    manufacturer: Optional[str]
    os_info: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[AssetResponse])
def get_assets(
    search: Optional[str] = Query(None, description="자산명, IP, 위치 검색"),
    db: Session = Depends(get_db)
):
    """자산 목록 조회 (검색 가능)"""
    query = db.query(Asset)
    
    if search:
        query = query.join(NetworkInterface, isouter=True).filter(
            or_(
                Asset.name.ilike(f"%{search}%"),
                Asset.asset_tag.ilike(f"%{search}%"),
                NetworkInterface.ip_address.ilike(f"%{search}%")
            )
        ).distinct()
    
    return query.all()


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """자산 상세 조회"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


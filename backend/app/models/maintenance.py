from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import date
import enum
from app.core.database import Base


class CheckType(str, enum.Enum):
    DISK = "Disk"
    PROCESS = "Process"
    LOG = "Log"
    OTHER = "Other"


class ResultStatus(str, enum.Enum):
    PASS = "Pass"
    FAIL = "Fail"


class MaintenanceLog(Base):
    """점검 이력 (Header)"""
    __tablename__ = "maintenance_logs"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    check_date = Column(Date, nullable=False, index=True)
    check_type = Column(Enum(CheckType), nullable=False)
    worker = Column(String(100), nullable=True)
    result_status = Column(Enum(ResultStatus), default=ResultStatus.PASS)

    # Relationships
    asset = relationship("Asset", back_populates="maintenance_logs")
    details = relationship("MaintenanceDetail", back_populates="log", cascade="all, delete-orphan")
    log_files = relationship("LogFile", back_populates="log", cascade="all, delete-orphan")


class MaintenanceDetail(Base):
    """상세 데이터 (Rows)"""
    __tablename__ = "maintenance_details"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("maintenance_logs.id"), nullable=False)
    item_name = Column(String(255), nullable=False)  # 예: "SysLog Level 1 Count", "CPU Usage"
    value = Column(String(255), nullable=True)  # 측정값
    raw_data = Column(JSON, nullable=True)  # JSON/Text 상세 내역

    log = relationship("MaintenanceLog", back_populates="details")


class LogFile(Base):
    """증빙 파일"""
    __tablename__ = "log_files"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("maintenance_logs.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # evtx, txt, conf

    log = relationship("MaintenanceLog", back_populates="log_files")


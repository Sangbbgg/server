from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class AssetStatus(str, enum.Enum):
    OPERATIONAL = "운영"
    MAINTENANCE = "점검"
    FAULTY = "불량"


class Asset(Base):
    """장비 마스터"""
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    asset_tag = Column(String(100), nullable=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)  # 호스트명/설비명
    model = Column(String(255), nullable=True)
    manufacturer = Column(String(255), nullable=True)
    os_info = Column(String(255), nullable=True)
    status = Column(Enum(AssetStatus), default=AssetStatus.OPERATIONAL)
    specs_cpu = Column(String(255), nullable=True)
    specs_memory = Column(String(255), nullable=True)
    specs_disk = Column(String(255), nullable=True)

    # Relationships
    system = relationship("System", back_populates="assets")
    location = relationship("Location", back_populates="assets")
    network_interfaces = relationship("NetworkInterface", back_populates="asset", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="asset", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="asset")


class NetworkInterface(Base):
    """네트워크 인터페이스 (1:N)"""
    __tablename__ = "network_interfaces"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 지원
    mac_address = Column(String(17), nullable=True)
    interface_name = Column(String(100), nullable=True)

    asset = relationship("Asset", back_populates="network_interfaces")


class Account(Base):
    """접속 계정 (1:N)"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)  # Bcrypt 암호화
    role = Column(String(50), nullable=True)

    asset = relationship("Asset", back_populates="accounts")


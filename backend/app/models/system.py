from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class System(Base):
    """설비 계층 (기능적 분류)"""
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("systems.id"), nullable=True)
    description = Column(Text, nullable=True)

    # Self-referential relationship
    children = relationship("System", backref="parent", remote_side=[id])
    assets = relationship("Asset", back_populates="system")


class Location(Base):
    """위치 계층 (물리적 분류)"""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    description = Column(Text, nullable=True)

    # Self-referential relationship
    children = relationship("Location", backref="parent", remote_side=[id])
    assets = relationship("Asset", back_populates="location")


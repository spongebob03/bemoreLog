from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import relationship
from typing import List
from typing import TYPE_CHECKING

from .base import Base

# SQLAlchemy Model
class Epic(Base):
    __tablename__ = "epics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String)
    depth = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    core_epic_id = Column(Integer, ForeignKey("epics.id"), nullable=True)

    # One to many relationship with sub_epics
    subs = relationship("Epic", backref="core_epic", remote_side=[id])

class EpicRelation(Base):
    __tablename__ = "epic_relations"
    id = Column(Integer, primary_key=True, index=True)
    core_epic_id = Column(Integer, ForeignKey("epics.id"), nullable=False)
    sub_epic_id = Column(Integer, ForeignKey("epics.id"), nullable=False)
    position_row = Column(Integer, nullable=False)
    position_col = Column(Integer, nullable=False)
    depth = Column(Integer, nullable=False, default=1)

# Pydantic Models
class EpicBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str

class EpicCreate(EpicBase):
    core_epic_id: Optional[int] = None

class EpicResponse(EpicBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class EpicRelationCreate(BaseModel):
    core_epic_id: int
    sub_epic_id: int
    position_row: int
    position_col: int
    depth: int = 1


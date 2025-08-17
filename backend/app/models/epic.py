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
    position = Column(Integer, nullable=True)  # 3x3 그리드 내 시계방향 위치 (0: 중앙, 1-8: 주변)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    core_epic_id = Column(Integer, ForeignKey("epics.id"), nullable=True)

    # One to many relationship with sub_epics
    # core_epic_id가 자신의 id인 epic들을 subs로 가져옴
    subs = relationship(
        "Epic",
        foreign_keys=[core_epic_id]
    )
    
    # Many to one relationship with core epic
    core_epic = relationship(
        "Epic",
        foreign_keys=[core_epic_id],
        remote_side=[id]
    )

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
    position: Optional[int] = None

class EpicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    depth: Optional[int] = None
    position: Optional[int] = None
    core_epic_id: Optional[int] = None

class EpicResponse(EpicBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    depth: int = 0
    position: Optional[int] = None
    core_epic_id: Optional[int] = None
    subs: List["EpicResponse"] = []

    class Config:
        orm_mode = True

class EpicRelationCreate(BaseModel):
    core_epic_id: int
    sub_epic_id: int
    position_row: int
    position_col: int
    depth: int = 1

# Epic 객체를 EpicResponse로 변환하는 함수
def to_epic_response(epic: "Epic") -> EpicResponse:
    # subs가 None이거나 예상과 다른 형태일 때를 대비하여 안전하게 처리
    subs_list = []
    if hasattr(epic, 'subs') and epic.subs is not None:
        try:
            subs_list = [to_epic_response(sub) for sub in epic.subs]
        except Exception as e:
            print(f"Warning: Error processing subs for epic {epic.id}: {e}")
            subs_list = []
    
    return EpicResponse(
        id=epic.id,
        title=epic.title,
        description=epic.description,
        status=epic.status,
        depth=epic.depth,
        position=epic.position,
        core_epic_id=epic.core_epic_id,
        created_at=epic.created_at,
        updated_at=epic.updated_at,
        subs=subs_list
    )

EpicResponse.update_forward_refs()


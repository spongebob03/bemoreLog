from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

from .base import Base


class HabitStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

# SQLAlchemy Model
class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    epic_id = Column(Integer, ForeignKey("epics.id"), nullable=True)  # 1:N 관계 (확장성)

    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)

    schedule = Column(String)  # cron 표현식 (예: "0 9 * * *" = 매일 오전 9시)
    target_count = Column(Integer, default=1)  # 목표 횟수 (예: 하루에 3번, 주에 5번)
    status = Column(String, default=HabitStatus.ACTIVE.value)
    current_combo = Column(Integer, default=0)  # 현재 연속 달성 일수
    best_combo = Column(Integer, default=0)  # 최고 연속 달성 일수
    total_completions = Column(Integer, default=0)  # 총 완료 횟수
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 1:N relationship with HabitCommit
    commits = relationship("HabitCommit", back_populates="habit")
    
    # Many to one relationship with Epic
    epic = relationship("Epic", back_populates="habits")

class HabitCommit(Base):
    __tablename__ = "habit_commits"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)  # habits 테이블과의 foreign key
    
    description = Column(Text, nullable=True)  # 선택적 메모
    effort = Column(Integer, nullable=False)  # 1-5 사이의 값
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Many to one relationship with Habit
    habit = relationship("Habit", back_populates="commits")

# Pydantic Models
class HabitBase(BaseModel):
    title: str
    description: Optional[str] = None
    schedule: Optional[str] = None  # cron 표현식
    target_count: int = 1
    epic_id: Optional[int] = None  # Epic 없이도 독립적인 습관 가능

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[str] = None
    target_count: Optional[int] = None
    status: Optional[HabitStatus] = None
    epic_id: Optional[int] = None  # 업데이트 시에는 선택적

class HabitResponse(HabitBase):
    id: int
    status: HabitStatus
    current_combo: int = 0
    best_combo: int = 0
    total_completions: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class HabitCommitBase(BaseModel):
    habit_id: int
    description: Optional[str] = None
    effort: int  # 1-5 사이의 값

class HabitCommitCreate(HabitCommitBase):
    pass

class HabitCommitUpdate(BaseModel):
    description: Optional[str] = None
    effort: Optional[int] = None

class HabitCommitResponse(HabitCommitBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Utility functions
def to_habit_response(habit: "Habit") -> HabitResponse:
    return HabitResponse(
        id=habit.id,
        title=habit.title,
        description=habit.description,
        schedule=habit.schedule,
        target_count=habit.target_count,
        epic_id=habit.epic_id,
        status=HabitStatus(habit.status),
        current_combo=habit.current_combo,
        best_combo=habit.best_combo,
        total_completions=habit.total_completions,
        created_at=habit.created_at,
        updated_at=habit.updated_at
    )

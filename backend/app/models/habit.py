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
    epic_id = Column(Integer, ForeignKey("epics.id"), nullable=True)

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
    epic = relationship("Epic", foreign_keys=[epic_id])

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

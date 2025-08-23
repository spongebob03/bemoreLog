from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.session import get_db
from ..models.habit import (
    HabitCreate, 
    HabitUpdate, 
    HabitResponse,
    HabitCommitCreate,
    HabitCommitResponse,
    HabitStatus
)
from ..services.habit import HabitService

router = APIRouter(
    prefix="/api/habit",
    tags=["habits"]
)

class HabitController:
    def __init__(self, db: Session):
        self.service = HabitService(db)

@router.post("/", response_model=HabitResponse)
async def create_habit(
    habit: HabitCreate,
    db: Session = Depends(get_db)
):
    """새로운 습관 생성"""
    controller = HabitController(db)
    return controller.service.create_habit(habit)

@router.get("/", response_model=List[HabitResponse])
async def get_habits(
    epic_id: Optional[int] = Query(None, description="특정 Epic에 속한 습관들만 조회"),
    status: Optional[HabitStatus] = Query(None, description="특정 상태의 습관들만 조회"),
    db: Session = Depends(get_db)
):
    """습관 목록 조회"""
    controller = HabitController(db)
    return controller.service.get_habits(epic_id=epic_id, status=status)

@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: int,
    db: Session = Depends(get_db)
):
    """특정 습관 조회"""
    controller = HabitController(db)
    habit = controller.service.get_habit(habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: int,
    habit: HabitUpdate,
    db: Session = Depends(get_db)
):
    """습관 정보 업데이트"""
    controller = HabitController(db)
    updated_habit = controller.service.update_habit(habit_id, habit)
    if not updated_habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return updated_habit

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: int,
    db: Session = Depends(get_db)
):
    """습관 삭제"""
    controller = HabitController(db)
    success = controller.service.delete_habit(habit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"message": "Habit deleted successfully"}

@router.post("/{habit_id}/commit", response_model=HabitCommitResponse)
async def create_habit_commit(
    habit_id: int,
    commit: HabitCommitCreate,
    db: Session = Depends(get_db)
):
    """습관 실천 기록 생성"""
    # habit_id를 commit 데이터에 설정
    commit.habit_id = habit_id
    
    controller = HabitController(db)
    habit_commit = controller.service.create_habit_commit(commit)
    if not habit_commit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit_commit

@router.get("/{habit_id}/commits", response_model=List[HabitCommitResponse])
async def get_habit_commits(
    habit_id: int,
    limit: int = Query(50, description="조회할 최대 기록 수"),
    db: Session = Depends(get_db)
):
    """습관의 실천 기록 목록 조회"""
    controller = HabitController(db)
    
    # 먼저 습관이 존재하는지 확인
    habit = controller.service.get_habit(habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return controller.service.get_habit_commits(habit_id, limit)

@router.patch("/{habit_id}/status", response_model=HabitResponse)
async def update_habit_status(
    habit_id: int,
    status: HabitStatus,
    db: Session = Depends(get_db)
):
    """습관 상태만 업데이트 (편의 엔드포인트)"""
    controller = HabitController(db)
    habit_update = HabitUpdate(status=status)
    updated_habit = controller.service.update_habit(habit_id, habit_update)
    if not updated_habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return updated_habit

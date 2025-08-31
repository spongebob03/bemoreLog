from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.habit import (
    Habit, 
    HabitCommit,
    HabitCreate, 
    HabitUpdate, 
    HabitResponse,
    HabitCommitCreate,
    HabitCommitResponse,
    HabitStatus,
    to_habit_response
)

class HabitService:
    def __init__(self, db: Session):
        self.db = db

    def create_habit(self, habit_data: HabitCreate) -> HabitResponse:
        """새로운 습관 생성"""
        # Epic이 지정된 경우에만 존재 여부 확인
        if habit_data.epic_id is not None:
            from ..models.epic import Epic
            epic = self.db.query(Epic).filter(Epic.id == habit_data.epic_id).first()
            if not epic:
                raise ValueError(f"Epic with id {habit_data.epic_id} not found")
        
        db_habit = Habit(
            title=habit_data.title,
            description=habit_data.description,
            schedule=habit_data.schedule,
            target_count=habit_data.target_count,
            epic_id=habit_data.epic_id,
            status=HabitStatus.ACTIVE.value
        )
        
        self.db.add(db_habit)
        self.db.commit()
        self.db.refresh(db_habit)
        
        return to_habit_response(db_habit)

    def get_habit(self, habit_id: int) -> Optional[HabitResponse]:
        """ID로 습관 조회"""
        habit = self.db.query(Habit).filter(Habit.id == habit_id).first()
        if habit:
            return to_habit_response(habit)
        return None

    def get_habits(self, epic_id: Optional[int] = None, status: Optional[HabitStatus] = None) -> List[HabitResponse]:
        """습관 목록 조회 (Epic ID나 상태로 필터링 가능)"""
        query = self.db.query(Habit)
        
        if epic_id is not None:
            query = query.filter(Habit.epic_id == epic_id)
        
        if status is not None:
            query = query.filter(Habit.status == status.value)
        
        habits = query.all()
        return [to_habit_response(habit) for habit in habits]

    def update_habit(self, habit_id: int, habit_data: HabitUpdate) -> Optional[HabitResponse]:
        """습관 정보 업데이트"""
        habit = self.db.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            return None

        update_data = habit_data.dict(exclude_unset=True)
        
        # epic_id가 변경되는 경우 Epic 존재 여부만 확인
        if 'epic_id' in update_data and update_data['epic_id'] is not None:
            from ..models.epic import Epic
            
            new_epic_id = update_data['epic_id']
            epic = self.db.query(Epic).filter(Epic.id == new_epic_id).first()
            if not epic:
                raise ValueError(f"Epic with id {new_epic_id} not found")
        
        for field, value in update_data.items():
            if hasattr(habit, field):
                setattr(habit, field, value)

        self.db.commit()
        self.db.refresh(habit)
        
        return to_habit_response(habit)

    def delete_habit(self, habit_id: int) -> bool:
        """습관 삭제"""
        habit = self.db.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            return False

        # 연관된 HabitCommit들도 삭제
        self.db.query(HabitCommit).filter(HabitCommit.habit_id == habit_id).delete()
        
        self.db.delete(habit)
        self.db.commit()
        return True

    def create_habit_commit(self, commit_data: HabitCommitCreate) -> Optional[HabitCommitResponse]:
        """습관 실천 기록 생성"""
        # 해당 습관이 존재하는지 확인
        habit = self.db.query(Habit).filter(Habit.id == commit_data.habit_id).first()
        if not habit:
            return None

        db_commit = HabitCommit(
            habit_id=commit_data.habit_id,
            description=commit_data.description,
            effort=commit_data.effort
        )
        
        self.db.add(db_commit)
        
        # 습관 통계 업데이트
        habit.total_completions += 1
        # TODO: current_combo, best_combo 로직 구현 (날짜 기반)
        
        self.db.commit()
        self.db.refresh(db_commit)
        
        return HabitCommitResponse(
            id=db_commit.id,
            habit_id=db_commit.habit_id,
            description=db_commit.description,
            effort=db_commit.effort,
            created_at=db_commit.created_at,
            updated_at=db_commit.updated_at
        )

    def get_habit_commits(self, habit_id: int, limit: int = 50) -> List[HabitCommitResponse]:
        """습관의 실천 기록 목록 조회"""
        commits = (
            self.db.query(HabitCommit)
            .filter(HabitCommit.habit_id == habit_id)
            .order_by(HabitCommit.created_at.desc())
            .limit(limit)
            .all()
        )
        
        return [
            HabitCommitResponse(
                id=commit.id,
                habit_id=commit.habit_id,
                description=commit.description,
                effort=commit.effort,
                created_at=commit.created_at,
                updated_at=commit.updated_at
            )
            for commit in commits
        ]

    def update_habit_combo(self, habit_id: int):
        """습관의 연속 달성 일수 업데이트 (별도로 호출하거나 스케줄러에서 사용)"""
        # TODO: 날짜별 달성 기록을 확인하여 current_combo 계산
        # TODO: best_combo 업데이트
        pass

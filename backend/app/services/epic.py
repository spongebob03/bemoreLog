from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from ..models.epic import Epic, EpicCreate, EpicUpdate, EpicResponse, to_epic_response

class EpicService:
    def __init__(self, db: Session):
        self.db = db

    async def create_epic(self, epic: EpicCreate) -> EpicResponse:
        db_epic = Epic(**epic.dict())
        self.db.add(db_epic)
        self.db.commit()
        self.db.refresh(db_epic)
        return to_epic_response(db_epic)

    async def get_epics(self, skip: int = 0, limit: int = 100) -> List[EpicResponse]:
        epics = self.db.query(Epic).options(joinedload(Epic.subs)).offset(skip).limit(limit).all()
        return [to_epic_response(epic) for epic in epics]

    async def get_epic(self, epic_id: int) -> Optional[EpicResponse]:
        epic = self.db.query(Epic).options(joinedload(Epic.subs)).filter(Epic.id == epic_id).first()
        if epic:
            return to_epic_response(epic)
        return None 
    
    async def update_epic(self, epic_id: int, epic: EpicUpdate) -> EpicResponse:
        db_epic = self.db.query(Epic).filter(Epic.id == epic_id).first()
        if db_epic:
            # 값이 있는 필드만 기존 Epic 객체에 업데이트
            epic_data = epic.dict(exclude_unset=True)
            for field, value in epic_data.items():
                if hasattr(db_epic, field):
                    setattr(db_epic, field, value)
            
            # updated_at 필드를 현재 시간으로 설정
            from datetime import datetime
            db_epic.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(db_epic)
            return to_epic_response(db_epic)
        return None
    
    async def delete_epic(self, epic_id: int) -> EpicResponse:
        db_epic = self.db.query(Epic).filter(Epic.id == epic_id).first()
        if db_epic:
            self.db.delete(db_epic)
            self.db.commit()
            return to_epic_response(db_epic)
        return None
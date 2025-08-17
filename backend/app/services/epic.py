from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from ..models.epic import Epic, EpicCreate, EpicUpdate, EpicResponse, to_epic_response

class EpicService:
    def __init__(self, db: Session):
        self.db = db

    async def create_epic(self, epic: EpicCreate) -> EpicResponse:
        # core_epic_id가 있을 때 depth 값을 자동으로 설정
        epic_data = epic.dict()
        if epic.core_epic_id:
            core_epic = self.db.query(Epic).filter(Epic.id == epic.core_epic_id).first()
            epic_data['depth'] = core_epic.depth + 1 if core_epic else 0
        
        db_epic = Epic(**epic_data)
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
            # 하위 epic들도 함께 삭제
            self._delete_sub_epics(db_epic.id)
            
            # 메인 epic 삭제
            self.db.delete(db_epic)
            self.db.commit()
            return to_epic_response(db_epic)
        return None
    
    def _delete_sub_epics(self, epic_id: int):
        """하위 epic들을 재귀적으로 삭제합니다."""
        # 해당 epic을 상위 epic으로 하는 모든 하위 epic 조회
        sub_epics = self.db.query(Epic).filter(Epic.core_epic_id == epic_id).all()
        
        for sub_epic in sub_epics:
            # 재귀적으로 하위 epic들 삭제
            self._delete_sub_epics(sub_epic.id)
            # 하위 epic 삭제
            self.db.delete(sub_epic)
        
        print(f"Deleted {len(sub_epics)} sub epics for epic {epic_id}")
    
    async def delete_all_epics(self) -> dict:
        """모든 epic을 삭제합니다."""
        count = self.db.query(Epic).count()
        self.db.query(Epic).delete()
        self.db.commit()
        return {"message": f"All {count} epics deleted successfully"}
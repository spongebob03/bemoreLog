from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from ..models.epic import Epic, EpicCreate, EpicResponse, to_epic_response

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
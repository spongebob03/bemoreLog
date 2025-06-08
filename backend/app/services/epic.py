from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.epic import Epic, EpicCreate, EpicResponse

class EpicService:
    def __init__(self, db: Session):
        self.db = db

    async def create_epic(self, epic: EpicCreate) -> EpicResponse:
        db_epic = Epic(**epic.dict())
        self.db.add(db_epic)
        self.db.commit()
        self.db.refresh(db_epic)
        return db_epic

    async def get_epics(self, skip: int = 0, limit: int = 100) -> List[EpicResponse]:
        return self.db.query(Epic).offset(skip).limit(limit).all()

    async def get_epic(self, epic_id: int) -> Optional[EpicResponse]:
        return self.db.query(Epic).filter(Epic.id == epic_id).first() 
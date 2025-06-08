from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os

from ..db.models import Epic
from ..db.session import get_db
from ..schemas.epic import Epic as EpicSchema, EpicCreate

router = APIRouter(
    prefix="/api/epic",
    tags=["epics"]
)

def get_db_override():
    if os.getenv("TESTING"):
        from ...tests.conftest import TestingSessionLocal
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield from get_db()

@router.post("", response_model=EpicSchema)
def create_epic(epic: EpicCreate, db: Session = Depends(get_db_override)):
    try:
        db_epic = Epic(**epic.dict())
        db.add(db_epic)
        db.commit()
        db.refresh(db_epic)
        return db_epic
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[EpicSchema])
def read_epics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_override)):
    epics = db.query(Epic).offset(skip).limit(limit).all()
    return epics

@router.get("/{epic_id}", response_model=EpicSchema)
def read_epic(epic_id: int, db: Session = Depends(get_db_override)):
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic 
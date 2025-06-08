from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import get_db
import os

router = APIRouter(
    prefix="/api/epic",
    tags=["epics"]
)

def get_db_override():
    if os.getenv("TESTING"):
        from test_database import get_test_db
        return get_test_db
    return get_db

@router.post("", response_model=schemas.Epic)
def create_epic(epic: schemas.EpicCreate, db: Session = Depends(get_db_override)):
    try:
        db_epic = models.Epic(**epic.dict())
        db.add(db_epic)
        db.commit()
        db.refresh(db_epic)
        return db_epic
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[schemas.Epic])
def read_epics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_override)):
    epics = db.query(models.Epic).offset(skip).limit(limit).all()
    return epics

@router.get("/{epic_id}", response_model=schemas.Epic)
def read_epic(epic_id: int, db: Session = Depends(get_db_override)):
    epic = db.query(models.Epic).filter(models.Epic.id == epic_id).first()
    if epic is None:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic 
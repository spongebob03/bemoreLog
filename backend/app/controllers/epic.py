from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os

from ..db.session import get_db
from ..models.epic import Epic, EpicCreate, EpicUpdate, EpicResponse
from ..services.epic import EpicService

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

class EpicController:
    def __init__(self, db: Session):
        self.service = EpicService(db)

    async def create_epic(self, epic: EpicCreate) -> EpicResponse:
        try:
            return await self.service.create_epic(epic)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_epics(self, skip: int = 0, limit: int = 100) -> List[EpicResponse]:
        return await self.service.get_epics(skip, limit)

    async def get_epic(self, epic_id: int) -> EpicResponse:
        epic = await self.service.get_epic(epic_id)
        if epic is None:
            raise HTTPException(status_code=404, detail="Epic not found")
        return epic
    
    async def update_epic(self, epic_id: int, epic: EpicUpdate) -> EpicResponse:
        try:
            return await self.service.update_epic(epic_id, epic)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    async def delete_epic(self, epic_id: int) -> EpicResponse:
        try:
            return await self.service.delete_epic(epic_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def delete_all_epics(self) -> dict:
        try:
            return await self.service.delete_all_epics()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# Route handlers
@router.post("", response_model=EpicResponse)
async def create_epic(
    epic: EpicCreate,
    db: Session = Depends(get_db_override)
):
    controller = EpicController(db)
    return await controller.create_epic(epic)

@router.get("", response_model=List[EpicResponse])
async def read_epics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_override)
):
    controller = EpicController(db)
    return await controller.get_epics(skip, limit)

@router.get("/{epic_id}", response_model=EpicResponse)
async def read_epic(
    epic_id: int,
    db: Session = Depends(get_db_override)
):
    controller = EpicController(db)
    return await controller.get_epic(epic_id) 

@router.put("/{epic_id}", response_model=EpicResponse)
async def update_epic(
    epic_id: int,
    epic: EpicUpdate,
    db: Session = Depends(get_db_override)
):
    controller = EpicController(db)
    return await controller.update_epic(epic_id, epic)

@router.delete("/{epic_id}", response_model=EpicResponse)
async def delete_epic(
    epic_id: int,
    db: Session = Depends(get_db_override)
):
    controller = EpicController(db)
    return await controller.delete_epic(epic_id)

@router.delete("", response_model=dict)
async def delete_all_epics(
    db: Session = Depends(get_db_override)
):
    controller = EpicController(db)
    return await controller.delete_all_epics()
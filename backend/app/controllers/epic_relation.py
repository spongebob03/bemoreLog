from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.epic import EpicRelation, EpicRelationCreate, Epic
from ..db.session import get_db

router = APIRouter()

@router.post("/api/epic/relation")
def create_epic_relation(relation: EpicRelationCreate, db: Session = Depends(get_db)):
    db_relation = EpicRelation(**relation.dict())
    db.add(db_relation)
    db.commit()
    db.refresh(db_relation)
    return db_relation

@router.get("/api/epic/{core_epic_id}/subs")
def get_sub_epics(core_epic_id: int, db: Session = Depends(get_db)):
    relations = db.query(EpicRelation).filter(EpicRelation.core_epic_id == core_epic_id).all()
    result = []
    for rel in relations:
        sub_epic = db.query(Epic).filter(Epic.id == rel.sub_epic_id).first()
        if sub_epic:
            result.append({
                "sub_epic_id": rel.sub_epic_id,
                "title": sub_epic.title,
                "position_row": rel.position_row,
                "position_col": rel.position_col,
                "depth": rel.depth,
            })
    return result

@router.get("/api/epic/{sub_epic_id}/cores")
def get_core_epics(sub_epic_id: int, db: Session = Depends(get_db)):
    relations = db.query(EpicRelation).filter(EpicRelation.sub_epic_id == sub_epic_id).all()
    result = []
    for rel in relations:
        core_epic = db.query(Epic).filter(Epic.id == rel.core_epic_id).first()
        if core_epic:
            result.append({
                "core_epic_id": rel.core_epic_id,
                "title": core_epic.title,
                "position_row": rel.position_row,
                "position_col": rel.position_col,
                "depth": rel.depth,
            })
    return result
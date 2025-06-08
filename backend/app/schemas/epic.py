from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EpicBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str

class EpicCreate(EpicBase):
    pass

class Epic(EpicBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 
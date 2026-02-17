from pydantic import BaseModel
from datetime import datetime


class WellResponse(BaseModel):
    id: int
    name: str
    original_filename: str
    created_at: datetime

    class Config:
        from_attributes = True

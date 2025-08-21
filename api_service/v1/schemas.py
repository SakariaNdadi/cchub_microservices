from datetime import datetime

from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    description: str | None = None
    status: str
    remind_at: datetime
    location_name: str
    profile_id: int


class TodoSchema(TodoBase):
    id: int
    status: str

    class Config:
        from_attributes = True


class TodoCreate(TodoBase):
    pass

from datetime import datetime

from pydantic import BaseModel


class EventBase(BaseModel):
    title: str


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    image: str
    created_at: datetime

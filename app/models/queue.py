from pydantic import BaseModel


class QueueBase(BaseModel):
    title: str


class QueueCreate(QueueBase):
    station_id: int


class Queue(QueueBase):
    id: int
    current_position: int

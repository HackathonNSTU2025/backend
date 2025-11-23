from pydantic import BaseModel


class StationBase(BaseModel):
    title: str
    description: str


class StationCreate(StationBase):
    event_id: int


class Station(StationBase):
    id: int

from typing import Optional

from app.models.queue import Queue
from app.models.station import Station, StationCreate
from app.repositories.station_repository import StationRepository


class StationService:
    def __init__(self, station_repository: StationRepository):
        self.repository = station_repository

    async def create(self, data: StationCreate) -> Station:
        station_data = StationCreate(
            event_id=data.event_id,
            title=data.title,
            description=data.description,
        )
        return await self.repository.create(station_data)

    async def get_least_loaded_queue(self, station_id: int) -> Optional[Queue]:
        return await self.repository.get_least_loaded_queue(station_id)

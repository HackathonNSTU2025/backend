from app.models.event import Event, EventCreate
from app.repositories.event_repository import EventRepository


class EventService:
    def __init__(self, event_repository: EventRepository):
        self.repository = event_repository

    async def create(self, data: EventCreate) -> Event:
        event_data = EventCreate(
            title=data.title,
        )
        return await self.repository.create(event_data)

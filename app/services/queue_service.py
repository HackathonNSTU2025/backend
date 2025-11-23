from app.models.queue import Queue, QueueCreate
from app.repositories.queue_repository import QueueRepository


class QueueService:
    def __init__(self, queue_repository: QueueRepository):
        self.repository = queue_repository

    async def create(self, data: QueueCreate) -> Queue:
        queue_data = QueueCreate(
            station_id=data.station_id,
            title=data.title,
        )
        return await self.repository.create(queue_data)

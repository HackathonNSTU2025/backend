from app.models.queue_entry import QueueEntry, QueueEntryCreate
from app.repositories.queue_entry_repository import QueueEntryRepository


class QueueEntryService:
    def __init__(self, queue_entry_repository: QueueEntryRepository):
        self.repository = queue_entry_repository

    async def create(self, data: QueueEntryCreate) -> QueueEntry:
        queue_entry_data = QueueEntryCreate(
            user_id=data.user_id,
            queue_id=data.queue_id,
        )
        return await self.repository.create(queue_entry_data)

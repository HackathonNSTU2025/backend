from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.queue_entry import QueueEntryCreate
from app.repositories.queue_entry_repository import QueueEntryRepository
from app.services.queue_entry_service import QueueEntryService

router = APIRouter(prefix="/queues", tags=["queues"])


async def get_queue_entries_service(request: Request) -> QueueEntryService:
    queue_entry_repository = QueueEntryRepository(request.app.state.database_pool)
    return QueueEntryService(queue_entry_repository)


@router.post(
    "/join",
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой записи очереди",
)
async def join(
    queue_entry_in: QueueEntryCreate,
    service: QueueEntryService = Depends(get_queue_entries_service),
):
    try:
        queue_entry = await service.create(queue_entry_in)
        return queue_entry
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

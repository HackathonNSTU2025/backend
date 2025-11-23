from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.queue import QueueCreate
from app.repositories.queue_repository import QueueRepository
from app.services.queue_service import QueueService

router = APIRouter(prefix="/queues", tags=["queues"])


async def get_queue_service(request: Request) -> QueueService:
    queue_repository = QueueRepository(request.app.state.database_pool)
    return QueueService(queue_repository)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой очереди",
)
async def create_queue(
    queue_in: QueueCreate, service: QueueService = Depends(get_queue_service)
):
    try:
        queue = await service.create(queue_in)
        return queue
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

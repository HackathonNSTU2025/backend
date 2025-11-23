from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.event import EventCreate
from app.repositories.event_repository import EventRepository
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


async def get_event_service(request: Request) -> EventService:
    event_repository = EventRepository(request.app.state.database_pool)
    return EventService(event_repository)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового события",
)
async def create_event(
    event_in: EventCreate, service: EventService = Depends(get_event_service)
):
    try:
        event = await service.create(event_in)
        return event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

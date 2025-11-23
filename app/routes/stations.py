from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.station import StationCreate
from app.repositories.station_repository import StationRepository
from app.services.station_service import StationService

router = APIRouter(prefix="/stations", tags=["stations"])


async def get_stations_service(request: Request) -> StationService:
    station_repository = StationRepository(request.app.state.database_pool)
    return StationService(station_repository)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой станции",
)
async def create_station(
    station_in: StationCreate, service: StationService = Depends(get_stations_service)
):
    try:
        station = await service.create(station_in)
        return station
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

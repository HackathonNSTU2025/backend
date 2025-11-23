from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


async def get_user_service(request: Request) -> UserService:
    user_repository = UserRepository(request.app.state.database_pool)
    return UserService(user_repository)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового пользователя",
)
async def create_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    try:
        user = await service.register(user_in)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer

from app.misc.jwt import get_user_id_from_token
from app.models.auth import LoginData, Token
from app.models.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer()


def get_auth_service(request: Request) -> AuthService:
    return AuthService(request.app.state.database_pool)


@router.post("/login", response_model=Token)
async def login(
    data: LoginData,
    auth_service=Depends(get_auth_service),
):
    return await auth_service.login(
        data.email,
        data.password,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, auth_service=Depends(get_auth_service)):
    return await auth_service.register(
        user_in.email,
        user_in.username,
        user_in.password,
    )


def get_user_repository(request: Request):
    return UserRepository(request.app.state.database_pool)


@router.get("/me")
async def get_me(
    token=Depends(bearer_scheme), user_repository=Depends(get_user_repository)
):
    user_id = get_user_id_from_token(token.credentials)

    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user

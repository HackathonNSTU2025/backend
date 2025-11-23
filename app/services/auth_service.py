from datetime import timedelta

from asyncpg import Pool
from fastapi import HTTPException, status

from app.misc.jwt import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.auth import Token
from app.models.user import User, UserCreate
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, pool: Pool):
        self.user_repository = UserRepository(pool)

    async def login(self, email: str, password: str) -> Token:
        user = await self.user_repository.get_by_email(email)

        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")

    async def register(self, email: str, username: str, password: str) -> User:
        existing = await self.user_repository.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        return await self.user_repository.create(
            UserCreate(
                email=email,
                username=username,
                password=get_password_hash(password),
            )
        )

from argon2 import PasswordHasher

from app.models.user import User, UserCreate
from app.repositories.user_repository import UserRepository

hasher = PasswordHasher()


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.repository = user_repository

    async def register(self, data: UserCreate) -> User:
        user_data = UserCreate(
            email=data.email,
            username=data.username,
            password=hasher.hash(data.password),
        )
        return await self.repository.create(user_data)

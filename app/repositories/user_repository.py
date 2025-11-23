from typing import Optional

import asyncpg

from app.misc.read_sql_query import read_sql_query
from app.models.user import User, UserCreate

DEFAULT_PROFILE_PHOTO = "anonymous.webp"

DOMAIN = "users"


class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, user_create: UserCreate) -> User:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "create"),
                user_create.email,
                user_create.username,
                user_create.password,
                DEFAULT_PROFILE_PHOTO,
            )
            return User(**dict(row))

    async def get_by_id(self, user_id: int) -> Optional[User]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "get_by_id"),
                user_id,
            )
            return User(**dict(row)) if row else None

    async def get_by_email(self, email: str) -> Optional[User]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "get_by_email"),
                email,
            )
            return User(**dict(row)) if row else None

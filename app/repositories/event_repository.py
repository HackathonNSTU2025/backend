from typing import Optional

import asyncpg

from app.misc.read_sql_query import read_sql_query
from app.models.event import Event, EventCreate

DEFAULT_EVENT_IMAGE = "event_default.webp"

DOMAIN = "events"


class EventRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, event_create: EventCreate) -> Event:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "create"),
                event_create.title,
                DEFAULT_EVENT_IMAGE,
            )
            return Event(**dict(row))

    async def get_by_id(self, event_id: int) -> Optional[Event]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "get_by_id"),
                event_id,
            )
            return Event(**dict(row)) if row else None

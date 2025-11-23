from typing import Optional

import asyncpg

from app.misc.read_sql_query import read_sql_query
from app.models.station import Station, StationCreate

DOMAIN = "stations"


class StationRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, station_create: StationCreate) -> Station:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "create"),
                station_create.event_id,
                station_create.title,
                station_create.description,
            )
            return Station(**dict(row))

    async def get_by_id(self, station_id: int) -> Optional[Station]:
        async with self.pool.acquire() as conn:
            row = await conn.fetch(
                read_sql_query(DOMAIN, "get_by_id"),
                station_id,
            )
            return Station(**dict(row))

    async def get_all_by_event_id(self, event_id: int) -> list[Station]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                read_sql_query(DOMAIN, "get_all_by_event_id"),
                event_id,
            )
            return [Station(**dict(row)) for row in rows]

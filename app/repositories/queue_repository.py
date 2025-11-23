import asyncpg

from app.misc.read_sql_query import read_sql_query
from app.models.queue import Queue, QueueCreate

DOMAIN = "queues"


class QueueRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, queue_create: QueueCreate) -> Queue:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "create"),
                queue_create.station_id,
                queue_create.title,
            )
            return Queue(**dict(row))

    async def get_all_by_station_id(self, station_id: int) -> list[Queue]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                read_sql_query(DOMAIN, "get_all_by_station_id"),
                station_id,
            )
            return [Queue(**dict(row)) for row in rows]

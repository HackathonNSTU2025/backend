import asyncpg
from typing_extensions import Optional

from app.misc.read_sql_query import read_sql_query
from app.models.queue_entry import QueueEntry, QueueEntryCreate

DOMAIN = "queue_entries"


class QueueEntryRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, queue_entry_create: QueueEntryCreate) -> QueueEntry:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "create"),
                queue_entry_create.user_id,
                # queue_id не передается, а должен быть получен
                # (берем все очереди, принадлежащие станции со station_id, затем выбираем из них наименее загруженную)
                # queue_entry_create.queue_id,
            )
            return QueueEntry(**dict(row))

    async def get_by_user_and_station_ids(
        self, user_id: int, station_id: int
    ) -> Optional[QueueEntry]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                read_sql_query(DOMAIN, "get_by_user_and_station_ids"),
                user_id,
                station_id,
            )
            return QueueEntry(**dict(row))

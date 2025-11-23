import logging
import os.path
from os import listdir

import asyncpg
from asyncpg.exceptions import UndefinedTableError
from asyncpg.pool import PoolAcquireContext

from app.settings import settings

logger = logging.getLogger("uvicorn")


async def get_current_schema_version(conn: PoolAcquireContext) -> int:
    try:
        schema_version = await conn.fetchval(  # pyright: ignore (ругается, что метода не существует, по факту существует)
            "SELECT MAX(version) FROM schema_migrations"
        )
        return schema_version if schema_version is not None else -1

    except UndefinedTableError:
        return -1


async def apply_migration(conn: PoolAcquireContext, sql_path: str, version: int):
    # читаем файл миграции, исполняем его
    with open(sql_path) as sql_file:
        await conn.execute(sql_file.read())  # pyright: ignore (ругается, что метода не существует, по факту существует)

    # обновляем версию схемы
    await conn.execute("INSERT INTO schema_migrations (version) VALUES ($1)", version)  # pyright: ignore (ругается, что метода не существует, по факту существует)

    logger.debug(f"database: migrations: applied {sql_path}")


async def apply_migrations(conn: PoolAcquireContext):
    current_version = await get_current_schema_version(conn)
    logger.debug(f"database: migrations: {current_version=}")

    for migration_file in sorted(listdir(settings.migrations_dir)):
        migration_version = int(migration_file[:6])

        if migration_version <= current_version:
            continue

        async with conn.transaction():  # pyright: ignore (ругается, что метода не существует, по факту существует)
            await apply_migration(
                conn,
                os.path.join(settings.migrations_dir, migration_file),
                migration_version,
            )


async def get_pool() -> asyncpg.Pool:
    pool: asyncpg.Pool = await asyncpg.create_pool(settings.database_dsn)
    logger.debug("database: pool was created")

    async with pool.acquire() as conn:
        await apply_migrations(conn)

    return pool

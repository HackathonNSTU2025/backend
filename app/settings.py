import logging
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

logger = logging.getLogger("uvicorn")

# загружаем переменные из .env
DOTENV_PATH = "./deploy/.env"
if not load_dotenv(DOTENV_PATH):
    logger.warning(f"env: load_dotenv({DOTENV_PATH}) failed!")


# получаем значение переменной окружения; если не задано - падаем с ошибкой
def mustgetenv(key: str) -> str:
    value = os.getenv(key)

    if not value:
        raise Exception(f"env: key '{key}' is not defined!")

    return value


# настройки проекта
class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    database_dsn: str = mustgetenv("DATABASE_DSN")
    migrations_dir: str = "./app/sql/migrations/"
    queries_dir: str = "./app/sql/queries/"
    static_dir: str = "./data/static/"
    log_level: str = logging.getLevelName(logging.DEBUG)


settings = Settings()

logger.setLevel(settings.log_level)
logger.debug(settings)

import os.path

from app.settings import settings


def read_sql_query(domain: str, func_name: str) -> str:
    with open(
        os.path.join(settings.queries_dir, domain, f"{func_name}.sql")
    ) as sql_file:
        return sql_file.read()

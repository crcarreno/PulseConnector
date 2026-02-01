from database.db import DB
from database.db_pool import MySQLAdapter, PostgresAdapter, MSSQLAdapter

ADAPTERS = {
    "mysql": MySQLAdapter,
    "postgres": PostgresAdapter,
    "mssql": MSSQLAdapter,
}

class DbPoolManager:

    def __init__(self, data_sources: list[dict], analytics):
        self.analytics = analytics
        self.adapters: dict[str, object] = {}

        for ds in data_sources:
            name = ds["name"]
            dialect = ds["dialect"]

            adapter_cls = ADAPTERS.get(dialect)
            if not adapter_cls:
                raise RuntimeError(f"Unsupported dialect '{dialect}'")

            self.adapters[name] = adapter_cls(ds, analytics)

    def get_db(self, name: str):
        try:
            adapter = self.adapters[name]
        except KeyError:
            raise RuntimeError(f"Data source '{name}' not found")

        return DB(adapter, self.analytics, adapter.dialect)

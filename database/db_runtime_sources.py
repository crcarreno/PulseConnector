from database.db_config import config_db

def load_runtime_sources():
    sources = {}

    rows = config_db.list_data_sources()

    for ds in rows:
        if not ds["is_active"]:
            continue

        sources[ds["name"]] = {
            "name": ds["name"],
            "dialect": ds["dialect_key"],
            "connection": {
                "host": ds["host"],
                "port": ds["port"],
                "user": ds["username"],
                "pass": ds["password"],
                "database": ds["database_name"],
            },
            "pool_size": 5,
        }

    return sources



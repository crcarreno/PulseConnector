from security.storage.sqlite_storage import SQLiteStorage
from pathlib import Path


class ConfigServices:

    def __init__(self):
        self.db = SQLiteStorage(Path("database/pulseconnector.db"))

    # ---------- DIALECTS ----------
    def list_dialects(self):
        return self.db.list_dialects()

    def get_dialect(self, dialect_id):
        return self.db.get_dialect(dialect_id)

    def create_dialect(self, id, key, name, supported_versions, is_active=True):
        self.db.create_dialect(
            id=id,
            key=key,
            name=name,
            supported_versions=supported_versions,
            is_active=is_active
        )

    def update_dialect(self, dialect_id, fields: dict):
        self.db.update_dialect(dialect_id, fields)

    def enable_disable_dialect(self, dialect_id, action):
        self.db.enable_disable_dialect(dialect_id, action)


    # ---------- DATA SOURCES ----------
    def list_data_sources(self):
        return self.db.list_data_sources()

    def get_data_source(self, data_source_id):
        return self.db.get_data_source(data_source_id)

    def create_data_source(
        self,
        id,
        name,
        dialect_id,
        host,
        port,
        username,
        password,
        database_name,
        is_active=True
    ):
        self.db.create_data_source(
            id=id,
            name=name,
            dialect_id=dialect_id,
            host=host,
            port=port,
            username=username,
            password=password,
            database_name=database_name,
            is_active=is_active
        )

    def update_data_source(self, data_source_id, fields: dict):
        self.db.update_data_source(data_source_id, fields)

    def delete_data_source(self, data_source_id):
        return self.db.delete_data_source(data_source_id)

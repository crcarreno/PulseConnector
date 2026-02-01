from pathlib import Path
from security.storage.sqlite_storage import SQLiteStorage

_DB_PATH = Path("database/pulseconnector.db")

config_db = SQLiteStorage(_DB_PATH)

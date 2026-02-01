
from abc import ABC, abstractmethod
from database.db import DB


class BaseSchemaExtractor(ABC):
    def __init__(self, connection):
        self.connection = connection

    @abstractmethod
    def get_tables(self):
        pass

    @abstractmethod
    def get_views(self):
        pass

    @abstractmethod
    def get_stored_procedures(self):
        pass


# ---------------- SQLITE ----------------
class SQLiteSchemaExtractor(BaseSchemaExtractor):
    def get_tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        return self._fetch(query)

    def get_views(self):
        query = "SELECT name FROM sqlite_master WHERE type='view';"
        return self._fetch(query)

    def get_stored_procedures(self):
        return []  # SQLite no soporta SP

    def _fetch(self, query):
        cur = self.connection.cursor()
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]


# ---------------- POSTGRESQL ----------------
class PostgresSchemaExtractor(BaseSchemaExtractor):

    def get_tables(self):
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type='BASE TABLE';
        """
        return self._fetch(query)

    def get_views(self):
        query = """
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema = 'public';
        """
        return self._fetch(query)

    def get_stored_procedures(self):
        query = """
        SELECT routine_name
        FROM information_schema.routines
        WHERE routine_type='PROCEDURE' AND routine_schema='public';
        """
        return self._fetch(query)

    def _fetch(self, query):
        cur = self.connection.cursor()
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]


# ---------------- MYSQL ----------------
class MySQLSchemaExtractor(BaseSchemaExtractor):
    def get_tables(self):
        query = "SHOW TABLES;"
        return self._fetch(query)

    def get_views(self):
        query = "SHOW FULL TABLES WHERE Table_type = 'VIEW';"
        return self._fetch(query)

    def get_stored_procedures(self):
        query = "SHOW PROCEDURE STATUS WHERE Db = DATABASE();"
        return self._fetch(query, index=1)

    def _fetch(self, query, index=0):
        cur = self.connection.cursor()
        cur.execute(query)
        return [row[index] for row in cur.fetchall()]


# ---------------- SQL SERVER ----------------
class SQLServerSchemaExtractor(BaseSchemaExtractor):
    def get_tables(self):
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE='BASE TABLE';
        """
        return self._fetch(query)

    def get_views(self):
        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.VIEWS;
        """
        return self._fetch(query)

    def get_stored_procedures(self):
        query = """
        SELECT name FROM sys.procedures;
        """
        return self._fetch(query)

    def _fetch(self, query):
        cur = self.connection.cursor()
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]


# ---------------- FACTORY ----------------
class SchemaExtractorFactory:

    @staticmethod
    def create(db: DB):

        conn = db.adapter.acquire()
        dialect = db.dialect

        if dialect == "sqlite":
            return SQLiteSchemaExtractor(conn)

        if dialect == "postgres":
            return PostgresSchemaExtractor(conn)

        if dialect == "mysql":
            return MySQLSchemaExtractor(conn)

        if dialect in ("mssql", "sqlserver"):
            return SQLServerSchemaExtractor(conn)

        raise ValueError(f"Unsupported database type: {dialect}")
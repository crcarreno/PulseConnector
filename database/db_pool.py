import pyodbc
import pymysql
import psycopg2
from queue import Queue, Empty
from analytics.logger import setup_logger

log = setup_logger()


class ConnectionPool:
    def __init__(self, factory, size=10):
        self.pool = Queue(maxsize=size)
        for _ in range(size):
            self.pool.put(factory())

    def acquire(self, timeout=5):
        try:
            return self.pool.get(timeout=timeout)
        except Empty:
            log.error("Timeout while acquiring connection")
            raise Exception("DB connection pool exhausted")

    def release(self, conn):
        self.pool.put(conn)


class MSSQLAdapter:

    def __init__(self, cfg: dict, analytics):
        try:
            self.analytics = analytics
            self.dialect = "mssql"

            self._conn_cfg = cfg["connection"]
            pool_size = cfg.get("pool_size", 10)

            self.pool = ConnectionPool(
                lambda: self._connect(),
                size=pool_size
            )

        except Exception as e:
            log.error(f"MSSQLAdapter init error: {e}")
            analytics.capture_error(
                e,
                component="MSSQLAdapter",
                extra={
                    "dialect": "mssql",
                    "operation": "init pool",
                    "data_source": cfg.get("name"),
                }
            )
            raise

    def _connect(self):
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={self._conn_cfg['host']},{self._conn_cfg['port']};"
            f"DATABASE={self._conn_cfg['database']};"
            f"UID={self._conn_cfg['user']};"
            f"PWD={self._conn_cfg['pass']};"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )

        return pyodbc.connect(conn_str, autocommit=True)

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)



class MySQLAdapter:

    def __init__(self, cfg: dict, analytics):
        self.analytics = analytics
        self.dialect = "mysql"

        self._conn_cfg = cfg["connection"]
        pool_size = cfg.get("pool_size", 10)

        self.pool = ConnectionPool(
            lambda: self._connect(),
            size=pool_size
        )

    def _connect(self):
        return pymysql.connect(
            host=self._conn_cfg["host"],
            port=self._conn_cfg["port"],
            user=self._conn_cfg["user"],
            password=self._conn_cfg["pass"],
            database=self._conn_cfg["database"],
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)


class PostgresAdapter:

    def __init__(self, cfg: dict, analytics):
        try:
            self.analytics = analytics
            self.dialect = "postgres"

            self._conn_cfg = cfg["connection"]
            pool_size = cfg.get("pool_size", 10)

            self.pool = ConnectionPool(
                lambda: self._connect(),
                size=pool_size
            )

        except Exception as e:
            log.error(f"PostgresAdapter init error: {e}")
            analytics.capture_error(
                e,
                component="PostgresAdapter",
                extra={
                    "dialect": "postgres",
                    "operation": "init pool",
                    "data_source": cfg.get("name"),
                }
            )
            raise

    def _connect(self):
        try:
            conn = psycopg2.connect(
                host=self._conn_cfg["host"],
                port=self._conn_cfg["port"],
                user=self._conn_cfg["user"],
                password=self._conn_cfg["pass"],
                dbname=self._conn_cfg["database"]
            )
            conn.autocommit = True
            return conn

        except Exception as e:
            log.error(f"PostgresAdapter connection error: {e}")
            self.analytics.capture_error(
                e,
                component="PostgresAdapter",
                extra={
                    "dialect": "postgres",
                    "operation": "connect",
                    "host": self._conn_cfg.get("host"),
                    "database": self._conn_cfg.get("database"),
                }
            )
            raise

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)

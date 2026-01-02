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

    def __init__(self, cfg, analytics):

        try:
            database = cfg["db_mssql"]
            odata = cfg["odata"]

            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={database['host']},{database['port']};"
                f"DATABASE={database['database']};"
                f"UID={database['user']};"
                f"PWD={database['pass']};"
                "Encrypt=no;"
                "TrustServerCertificate=yes;"
            )

            self.pool = ConnectionPool(
                lambda: pyodbc.connect(conn_str, autocommit=True),
                size=odata["pool_size"]
            )

        except Exception as e:
            log.error("Error: {}".format(e))
            analytics.capture_error(
                e,
                component="MSSQLAdapter",
                extra={
                    "dialect": "mssql",
                    "operation": "init connection",
                }
            )
            raise e

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)


class MySQLAdapter:

    def __init__(self, cfg, analytics):

        try:

            database = cfg["db_mysql"]
            odata = cfg["odata"]

            self.pool = ConnectionPool(
                lambda: pymysql.connect(
                    host=database["host"],
                    port=database["port"],
                    user=database["user"],
                    password=database["pass"],
                    database=database["database"],
                    autocommit=True,
                    cursorclass=pymysql.cursors.DictCursor
                ),
                size=odata["pool_size"]
            )
        except Exception as e:
            log.error("Error: {}".format(e))
            analytics.capture_error(
                e,
                component="MySQLAdapter",
                extra={
                    "dialect": "mysql",
                    "operation": "init connection",
                }
            )
            raise e

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)


class PostgresAdapter:

    def __init__(self, cfg, analytics):
        odata = cfg["odata"]

        self.pool = ConnectionPool(
            lambda: self._connect(cfg, analytics),
            size=odata["pool_size"]
        )

    def _connect(self, cfg, analytics):

        try:
            database = cfg["db_postgres"]

            conn = psycopg2.connect(
                host=database["host"],
                port=database["port"],
                user=database["user"],
                password=database["pass"],
                dbname=database["database"]
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            log.error("Error: {}".format(e))
            analytics.capture_error(
                e,
                component="Postgres",
                extra={
                    "dialect": "postgres",
                    "operation": "init connection",
                }
            )
            raise e

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)

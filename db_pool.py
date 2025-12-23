import pyodbc
import pymysql
import psycopg2


from queue import Queue, Empty

class ConnectionPool:

    def __init__(self, factory, size=10):
        self.pool = Queue(maxsize=size)
        for _ in range(size):
            self.pool.put(factory())

    def acquire(self, timeout=5):
        try:
            return self.pool.get(timeout=timeout)
        except Empty:
            raise Exception("DB connection pool exhausted")

    def release(self, conn):
        self.pool.put(conn)



class MSSQLAdapter:

    def __init__(self, cfg):
        conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={cfg['host']},{cfg['port']};"
            f"DATABASE={cfg['database']};"
            f"UID={cfg['user']};"
            f"PWD={cfg['pass']};"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )

        self.pool = ConnectionPool(
            lambda: pyodbc.connect(conn_str, autocommit=True),
            size=cfg.get("pool_size", 10)
        )

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)


class MySQLAdapter:

    def __init__(self, cfg):
        self.pool = ConnectionPool(
            lambda: pymysql.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["pass"],
                database=cfg["database"],
                autocommit=True,
                cursorclass=pymysql.cursors.DictCursor
            ),
            size=cfg.get("pool_size", 10)
        )

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)


class PostgresAdapter:

    def __init__(self, cfg):
        self.pool = ConnectionPool(
            lambda: self._connect(cfg),
            size=cfg.get("pool_size", 10)
        )

    def _connect(self, cfg):
        conn = psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["pass"],
            dbname=cfg["database"]
        )
        conn.autocommit = True
        return conn

    def acquire(self):
        return self.pool.acquire()

    def release(self, conn):
        self.pool.release(conn)

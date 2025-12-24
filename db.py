# db.py
from sqlalchemy import create_engine, MetaData, Table, select, text, insert, update, inspect
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any
from db_pool import MSSQLAdapter, MySQLAdapter, PostgresAdapter


class Meta:
    def __init__(self):
        self.tables = {}


class DB:

    def __init__(self, cfg):
        self.cfg = cfg
        self.meta = Meta()

        dialect = cfg["active_dialect"]

        if dialect == "mssql":
            self.adapter = MSSQLAdapter(cfg)

        elif dialect == "mysql":
            self.adapter = MySQLAdapter(cfg["db_mysql"])

        elif dialect == "postgres":
            self.adapter = PostgresAdapter(cfg["db_postgres"])

        else:
            raise ValueError("Unsupported dialect")

        self.load_metadata()


    def load_metadata(self):
        dialect = self.cfg["active_dialect"]
        conn = self.adapter.acquire()
        cur = None

        try:
            cur = conn.cursor()

            if dialect == "mssql":
                cur.execute("""
                            SELECT c.TABLE_NAME,
                                   c.COLUMN_NAME,
                                   c.DATA_TYPE,
                                   c.IS_NULLABLE,
                                   CASE WHEN k.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS IS_PK
                            FROM INFORMATION_SCHEMA.COLUMNS c
                                     LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
                                               ON c.TABLE_NAME = k.TABLE_NAME
                                                   AND c.COLUMN_NAME = k.COLUMN_NAME
                                                   AND OBJECTPROPERTY(
                                                               OBJECT_ID(k.CONSTRAINT_SCHEMA + '.' + k.CONSTRAINT_NAME),
                                                               'IsPrimaryKey'
                                                       ) = 1
                            ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
                            """)

            elif dialect == "mysql":
                cur.execute("""
                            SELECT c.TABLE_NAME,
                                   c.COLUMN_NAME,
                                   c.DATA_TYPE,
                                   c.IS_NULLABLE,
                                   CASE WHEN k.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS IS_PK
                            FROM INFORMATION_SCHEMA.COLUMNS c
                                     LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
                                               ON c.TABLE_SCHEMA = k.TABLE_SCHEMA
                                                   AND c.TABLE_NAME = k.TABLE_NAME
                                                   AND c.COLUMN_NAME = k.COLUMN_NAME
                                                   AND k.CONSTRAINT_NAME = 'PRIMARY'
                            WHERE c.TABLE_SCHEMA = DATABASE()
                            ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
                            """)

            elif dialect == "postgres":
                cur.execute("""
                            SELECT c.table_name,
                                   c.column_name,
                                   c.data_type,
                                   c.is_nullable,
                                   CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN 1 ELSE 0 END AS is_pk
                            FROM information_schema.columns c
                                     LEFT JOIN information_schema.key_column_usage k
                                               ON c.table_name = k.table_name
                                                   AND c.column_name = k.column_name
                                     LEFT JOIN information_schema.table_constraints tc
                                               ON k.constraint_name = tc.constraint_name
                            WHERE c.table_schema = 'public'
                            ORDER BY c.table_name, c.ordinal_position
                            """)

            rows = cur.fetchall()
            self.meta = self._build_meta(rows)

        finally:
            if cur:
                cur.close()
            self.adapter.release(conn)


    def _build_meta(self, rows):
        meta = Meta()

        for table, column, dtype, nullable, is_pk in rows:
            if table not in meta.tables:
                meta.tables[table] = {"columns": {}}

            meta.tables[table]["columns"][column] = {
                "type": dtype,
                "nullable": nullable in ("YES", "yes", True, 1),
                "pk": bool(is_pk)
            }

        return meta


    def execute(self, sql, params=None):
        conn = self.adapter.acquire()
        cur = None
        try:
            cur = conn.cursor()
            cur.execute(sql, params or [])
            return cur.fetchall()
        finally:
            if cur:
                cur.close()
            self.adapter.release(conn)


    def test_db_connection(self, conn_str: str) -> Dict[str, Any]:
        """
        Return:
            {
                "ok": True/False,
                "message": str,
                "exception": Exception | None
            }
        """
        engine = None
        try:
            engine = create_engine(conn_str, pool_pre_ping=True)

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            return {
                "ok": True,
                "message": "Success connection",
                "exception": None
            }

        except SQLAlchemyError as e:
            return {
                "ok": False,
                "message": "Connection error",
                "exception": e
            }

        finally:
            if engine:
                engine.dispose()


    def _debug_foreign_keys(self, engine):
        """
        Inspecciona todas las tablas y detecta errores en claves extranjeras.
        Útil para bases antiguas como Northwind donde algunas restricciones
        pueden tener nombres inválidos o campos inconsistentes.
        """

        inspector = inspect(engine)

        print("\n====== Debug de Foreign Keys ======")

        for table in inspector.get_table_names():
            print(f"\nTable: {table}")

            try:
                fks = inspector.get_foreign_keys(table)

                if not fks:
                    print("Without FKs – all ok.")
                    continue

                for fk in fks:
                    name = fk.get("name")
                    referred = fk.get("referred_table")
                    local_cols = fk.get("constrained_columns")
                    remote_cols = fk.get("referred_columns")

                    # Validación básica
                    if not name or name.strip() == "":
                        print(f"FK con nombre vacío o inválido → {fk}")
                    else:
                        print(f"FK: {name} → {referred} "
                              f"{local_cols} -> {remote_cols}")

            except Exception as e:
                print(f"Error return FKs of the table: {e}")


    def _debug_reflect(self, engine):
        
        #I use this function to check if there are database objects that cannot be read by reflect.
        

        inspector = inspect(engine)
        meta = MetaData()

        for table in inspector.get_table_names():
            try:
                print(f"Test table: {table}")
                meta.reflect(bind=engine, only=[table])
                print(f"OK: {table}")
            except Exception as e:
                print(f"Error in {table}: {e}")


    def get_table(self, table_name):
        try:
            if not self.meta or not self.meta.tables:
                raise RuntimeError("Database metadata not loaded")

            if table_name not in self.meta.tables:
                raise RuntimeError(f"Table '{table_name}' not found in metadata")

            return self.meta.tables[table_name]

        except Exception as e:
            raise RuntimeError(f"Error : {e}")


    def query_odata(self, table_name, params):
        table = self.get_table(table_name)
        columns = table["columns"]

        # ----- SELECT -----
        if "$select" in params:
            requested = [c.strip() for c in params["$select"].split(",")]
            valid = [c for c in requested if c in columns]
            if not valid:
                raise RuntimeError("No valid columns in $select")
            select_clause = ", ".join(valid)
        else:
            select_clause = ", ".join(columns.keys())

        sql = f"SELECT {select_clause} FROM {table_name}"
        sql_params = []

        # ----- WHERE ($filter) -----
        if "$filter" in params:
            where_sql, where_params = self._parse_filter(params["$filter"], columns)
            if where_sql:
                sql += f" WHERE {where_sql}"
                sql_params.extend(where_params)

        # ----- ORDER BY -----
        if "$orderby" in params:
            order_parts = []
            for part in params["$orderby"].split(","):
                part = part.strip()
                if " " in part:
                    col, direction = part.split()
                    direction = direction.upper()
                else:
                    col, direction = part, "ASC"

                if col in columns and direction in ("ASC", "DESC"):
                    order_parts.append(f"{col} {direction}")

            if order_parts:
                sql += " ORDER BY " + ", ".join(order_parts)

        # ----- LIMIT / OFFSET -----
        dialect = self.cfg["active_dialect"]

        top = int(params.get("$top", 0)) if "$top" in params else None
        skip = int(params.get("$skip", 0)) if "$skip" in params else None

        if top is not None:
            if dialect == "mssql":
                if "ORDER BY" not in sql.upper():
                    sql += " ORDER BY (SELECT 1)"
                sql += f" OFFSET {skip or 0} ROWS FETCH NEXT {top} ROWS ONLY"
            else:
                sql += f" LIMIT {top}"
                if skip:
                    sql += f" OFFSET {skip}"

        rows = self.execute(sql, sql_params)
        return {
            "columns": select_clause.split(", "),
            "rows": rows
        }


    def _parse_filter(self, filter_str, columns):
        ops = {
            "eq": "=",
            "ne": "!=",
            "gt": ">",
            "lt": "<",
            "ge": ">=",
            "le": "<=",
            "like": "LIKE"
        }

        clauses = []
        params = []

        parts = [p.strip() for p in filter_str.split(" and ")]

        for p in parts:
            tokens = p.split(" ", 2)
            if len(tokens) != 3:
                continue

            col, op, val = tokens
            if col not in columns or op not in ops:
                continue

            # limpiar comillas
            if (val.startswith("'") and val.endswith("'")) or \
                    (val.startswith('"') and val.endswith('"')):
                val = val[1:-1]

            clauses.append(f"{col} {ops[op]} %s")
            params.append(val)

        return (" AND ".join(clauses), params) if clauses else (None, None)

    def insert_odata(self, table_name, data: dict):
        table = self.get_table(table_name)
        columns = table["columns"]

        valid = {k: v for k, v in data.items() if k in columns}
        if not valid:
            raise RuntimeError("No valid columns to insert")

        cols = ", ".join(valid.keys())
        placeholders = ", ".join(["%s"] * len(valid))

        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

        self.execute(sql, list(valid.values()))
        return {"status": "ok"}


    def update_odata(self, table_name, key_column: str, key_value, data: dict):
        table = self.get_table(table_name)
        columns = table["columns"]

        if key_column not in columns:
            raise RuntimeError(f"Key column '{key_column}' not found")

        updates = []
        params = []

        for k, v in data.items():
            if k in columns and k != key_column:
                updates.append(f"{k} = %s")
                params.append(v)

        if not updates:
            raise RuntimeError("No valid columns to update")

        sql = (
            f"UPDATE {table_name} "
            f"SET {', '.join(updates)} "
            f"WHERE {key_column} = %s"
        )

        params.append(key_value)

        self.execute(sql, params)
        return {"status": "ok"}


    def test_connection(self):
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()

            return {"ok": True}

        except Exception as ex:
            return {
                "ok": False,
                "message": "Database connection failed",
                "exception": str(ex)
            }

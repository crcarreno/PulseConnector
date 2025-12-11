# db.py
from sqlalchemy import create_engine, MetaData, Table, select, text, insert, update, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import asc, desc
from urllib.parse import quote_plus
from typing import Dict, Any

def build_connection_string(cfg):

    active = cfg.get("active_dialect")

    if not active:
        raise Exception("No active dialect selected")

    db_section = None
    for key, val in cfg.items():
        if key.startswith("db_") and isinstance(val, dict) and val.get("dialect") == active:
            db_section = val
            break

    if not db_section:
        raise Exception(f"No database config found for dialect '{active}'")

    d = db_section
    dialect = d["dialect"]

    if dialect == "mysql":
        return (
            f"mysql+pymysql://{d['user']}:{quote_plus(d['pass'])}"
            f"@{d['host']}:{d['port']}/{d['database']}"
        )

    if dialect == "postgres":
        return (
            f"postgresql+psycopg2://{d['user']}:{quote_plus(d['pass'])}"
            f"@{d['host']}:{d['port']}/{d['database']}"
        )

    if dialect == "mssql":
        user = quote_plus(d['user'])
        pwd = quote_plus(d['pass'])
        host = d['host']
        port = d['port']
        db = d['database']

        driver = "ODBC Driver 18 for SQL Server"
        driver_q = quote_plus(driver)

        return (
            f"mssql+pyodbc://{user}:{pwd}@{host}:{port}/{db}"
            f"?driver={driver_q}&Encrypt=no&TrustServerCertificate=yes"
        )

    raise Exception(f"Dialect '{dialect}' not supported")


class DB:

    def __init__(self, cfg):

        try:
            self.conn_str = build_connection_string(cfg)

            result = self.test_db_connection(self.conn_str)

            if not result["ok"]:
                raise RuntimeError(
                    f"{result['message']}: {result['exception']}"
                )

            self.engine = create_engine(self.conn_str, pool_pre_ping=True)

            #self.debug_reflect(self.engine)
            #self.debug_foreign_keys(self.engine)
            self.meta = MetaData()
            self.meta.reflect(bind=self.engine)
        except Exception as e:
            raise RuntimeError(f"Error : {e}")


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
        Inspecciona todas las tablas y detecta errores en Foreign Keys.
        Útil para bases antiguas como Northwind donde algunos constraints
        pueden tener nombres inválidos o campos inconsistentes.
        """

        inspector = inspect(engine)

        print("\n====== Debug de Foreign Keys ======")

        for table in inspector.get_table_names():
            print(f"\n➡ Tabla: {table}")

            try:
                fks = inspector.get_foreign_keys(table)

                if not fks:
                    print("Sin FKs – todo ok.")
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
                print(f"Error al obtener FKs de la tabla: {e}")

        print("\n====== Fin del debug de FKs ======\n")


    def _debug_reflect(self, engine):
        '''
        Esta función la uso para verificar si existen objetos de bases que no pueden ser leídos por el reflect
        '''

        inspector = inspect(engine)
        meta = MetaData()

        for table in inspector.get_table_names():
            try:
                print(f"→ Probando tabla: {table}")
                meta.reflect(bind=engine, only=[table])
                print(f"   OK: {table}")
            except Exception as e:
                print(f"   ❌ Error en {table}: {e}")


    def get_table(self, table_name):
        try:
            if table_name not in self.meta.tables:
                self.meta.reflect(bind=self.engine, only=[table_name])
            return Table(table_name, self.meta, autoload_with=self.engine)
        except Exception as e:
            raise RuntimeError(f"Error : {e}")


    def query_odata(self, table_name, params):

        try:
            table = self.get_table(table_name)
            q = select(table)

            if "$select" in params:
                cols = [table.c[c] for c in params["$select"].split(",") if c in table.c]
                if cols:
                    q = select(*cols)
            # $filter simple - solo soporte AND y operadores eq, gt, lt, like
            if "$filter" in params:
                # filtro muy básico: "col eq value and other gt 3"
                expr = self._parse_filter(params["$filter"], table)
                if expr is not None:
                    q = q.where(expr)
            # $orderby
            if "$orderby" in params:
                ob = params["$orderby"]
                parts = [p.strip() for p in ob.split(",")]
                for p in parts:
                    if " " in p:
                        col, direction = p.split()
                    else:
                        col, direction = p, "asc"
                    if col in table.c:
                        q = q.order_by(asc(table.c[col]) if direction.lower()=="asc" else desc(table.c[col]))
            # $top / $skip
            if "$skip" in params:
                q = q.offset(int(params["$skip"]))
            if "$top" in params:
                q = q.limit(int(params["$top"]))
            return q
        except Exception as e:
            raise RuntimeError(f"Error : {e}")


    def _parse_filter(self, filter_str, table):

        ops = {
            "eq": lambda c, v: c == v,
            "ne": lambda c, v: c != v,
            "gt": lambda c, v: c > v,
            "lt": lambda c, v: c < v,
            "ge": lambda c, v: c >= v,
            "le": lambda c, v: c <= v,
            "like": lambda c, v: c.like(v)
        }

        clauses = []

        parts = [p.strip() for p in filter_str.split(" and ")]

        for p in parts:
            toks = p.split(" ")
            if len(toks) < 3:
                continue
            col = toks[0]
            op = toks[1]
            val = " ".join(toks[2:])
            # limpiar comillas
            if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
                val = val[1:-1]
            # convertir tipo si columna es numerica: intento simple
            if col in table.c:
                colobj = table.c[col]
                # intento convertir a int/float si corresponde
                try:
                    if colobj.type.python_type in (int,):
                        val_parsed = int(val)
                    elif colobj.type.python_type in (float,):
                        val_parsed = float(val)
                    else:
                        val_parsed = val
                except Exception:
                    val_parsed = val
                if op in ops:
                    clauses.append(ops[op](colobj, val_parsed))
        if clauses:
            from sqlalchemy import and_
            return and_(*clauses)
        return None


    def insert_odata(self, table_name, data: dict):

        try:
            table = self.get_table(table_name)
            stmt = insert(table).values(**data)

            with self.engine.begin() as conn:
                result = conn.execute(stmt)

                # Si la tabla tiene PK autoincremental, devolverla
                try:
                    return {"inserted_id": result.inserted_primary_key[0]}
                except:
                    return {"status": "ok"}

        except Exception as e:
            raise RuntimeError(f"Insert error: {e}")


    def update_odata(self, table_name, key_column: str, key_value, data: dict):

        try:
            table = self.get_table(table_name)

            if key_column not in table.c:
                raise Exception(f"Column '{key_column}' not found in table '{table_name}'")

            stmt = (
                update(table)
                .where(table.c[key_column] == key_value)
                .values(**data)
            )

            with self.engine.begin() as conn:
                result = conn.execute(stmt)
                return {"updated": result.rowcount}

        except Exception as e:
            raise RuntimeError(f"Update error: {e}")
# db.py
from sqlalchemy import create_engine, MetaData, Table, select, text
from sqlalchemy.sql import asc, desc
from urllib.parse import quote_plus


def build_connection_string(cfg):
    active = cfg.get("active_dialect")
    if not active:
        raise Exception("No active dialect selected")

    # Buscar la sección que coincida con ese dialecto
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
        odbc = quote_plus(
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server={d['host']},{d['port']};"
            f"Database={d['database']};"
            f"UID={d['user']};PWD={d['pass']};"
        )
        return f"mssql+pyodbc:///?odbc_connect={odbc}"

    raise Exception(f"Dialect '{dialect}' not supported")

class DB:
    def __init__(self, cfg):

        try:
            self.conn_str = build_connection_string(cfg)
            self.engine = create_engine(self.conn_str, pool_pre_ping=True)
            self.meta = MetaData()
            self.meta.reflect(bind=self.engine)
        except Exception as e:
            raise RuntimeError(f"Error : {e}")


    def get_table(self, table_name):
        try:
            if table_name not in self.meta.tables:
                # refrescar si no existe
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
        # Parser muy simple — soporta "col eq value" y combinaciones con "and"
        from sqlalchemy import and_, or_

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
            # ejemplo: name eq 'juan'  -> split en 3
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

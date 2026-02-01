import sqlite3
from pathlib import Path

class SQLiteStorage:

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()


    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        schema = Path("security/storage/schema.sql").read_text()
        with self._conn() as conn:
            conn.executescript(schema)

    def get_user_permissions(self, username):

        with self._conn() as c:
            rows = c.execute("""
                 SELECT DISTINCT
                        pa.endpoint_name,
                        pa.action
                    FROM permissions p
                    INNER JOIN permission_actions pa
                        ON pa.permission_uid = p.uid
                    INNER JOIN permission_subjects ps
                        ON ps.permission_uid = p.uid
                    LEFT JOIN group_users gu
                        ON ps.subject_type = 'group'
                       AND gu.group_name = ps.subject_id
                    WHERE p.active = 1
                      --AND (
                      --      (ps.subject_type = 'user' AND ps.subject_id = :username)
                      --      OR
                      --      (ps.subject_type = 'group' AND gu.user = :username)
                      --    );
                 """, ).fetchall()

            perms = {}
            for r in rows:
                perms.setdefault(r["endpoint_name"], set()).add(r["action"])

            return perms


    # ---------- USERS ----------

    def validate_user_credentials(self, user, password_hash):
        with self._conn() as c:
            row = c.execute("""
                            SELECT user, password_hash, active
                            FROM users
                            WHERE user = ?
                            """, (user,)).fetchone()

            if not row:
                return False, "User not found"

            if row["active"] != 1:
                return False, "User disabled"

            if row["password_hash"] != password_hash:
                return False, "Invalid credentials"

            return True, "OK"

    def list_users(self):
        with self._conn() as c:
            return c.execute("SELECT user, display_name FROM users").fetchall()


    def get_user(self, user):
        with self._conn() as c:
            row = c.execute(
                "SELECT user, display_name, active, password_hash FROM users WHERE user = ?", (user,)
            ).fetchone()
            if not row:
                raise ValueError("User not found")
            return row


    def create_user(self, user, display, password):
        with self._conn() as c:
            c.execute("""
                INSERT INTO users (user, display_name, password_hash)
                VALUES (?, ?, ?)
            """, (user, display, password))


    def update_user(self, user, fields: dict):
        keys = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [user]
        with self._conn() as c:
            cur = c.execute(
                f"UPDATE users SET {keys} WHERE user = ?", values
            )
            if cur.rowcount == 0:
                raise ValueError("User not found")


    def enable_disable_user(self, user, action):
        self.update_user(user, {"active": action})



    # ---------- GROUPS ----------

    def list_groups(self):
        with self._conn() as c:
            return c.execute("SELECT * FROM groups").fetchall()


    def create_group(self, group, display):
        with self._conn() as c:
            c.execute("""
                INSERT INTO groups (group_name, display_name)
                VALUES (?, ?)
            """, (group, display))


    def disable_group(self, group):
        with self._conn() as c:
            c.execute(
                "UPDATE groups SET active = 0 WHERE group_name = ?", (group,)
            )


    def add_user_to_group(self, group, user):
        with self._conn() as c:
            c.execute("""
                INSERT OR IGNORE INTO group_users (group_name, user)
                VALUES (?, ?)
            """, (group, user))


    def remove_user_from_group(self, group, user):
        with self._conn() as c:
            c.execute("""
                DELETE FROM group_users
                WHERE group_name=? AND user=?
            """, (group, user))

    def update_group(self, group, fields):
        keys = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [group]

        with self._conn() as c:
            cur = c.execute(
                f"UPDATE groups SET {keys} WHERE group_name=?",
                values
            )
            if cur.rowcount == 0:
                raise ValueError("Group not found")

    def enable_disable_group(self, group, action):
        with self._conn() as c:
            cur = c.execute(
                "UPDATE groups SET active=? WHERE group_name=?",
                (action, group)
            )
            if cur.rowcount == 0:
                raise ValueError("Group not found")

    def list_group_members(self, group):
        with self._conn() as c:
            rows = c.execute("""
                             SELECT u.user,
                                    u.display_name,
                                    u.active
                             FROM group_users gu
                                      INNER JOIN users u ON u.user = gu.user
                             WHERE gu.group_name = ?
                             """, (group,)).fetchall()

            return [dict(r) for r in rows]


    # ---------- ENDPOINTS ----------

    def list_endpoints(self):
        with self._conn() as c:
            return c.execute("""SELECT
                                en.name ,
                                en.namespace ,
                                en."type" ,
                                en.id_connection ,
                                en.primary_key ,
                                en.source , 
                                dl.name as name_dialect,
                                ds.database_name ,
                                ds.name as datasource
                                FROM endpoints en
                                join data_sources ds on ds.id = en.id_connection 
                                join dialects dl on dl.id = ds.dialect_id 
                                """).fetchall()

    def register_endpoint(self, ep: dict):
        with self._conn() as c:
            c.execute("""
                INSERT INTO endpoints
                (name, id_connection, type, source, namespace, primary_key)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ep["name"], ep["id_connection"],
                ep["type"], ep["source"], ep["namespace"],
                ep.get("primary_key", "")
            ))

    def update_endpoint(self, name, fields):
        keys = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [name]

        with self._conn() as c:
            cur = c.execute(
                f"UPDATE endpoints SET {keys} WHERE name=?",
                values
            )
            if cur.rowcount == 0:
                raise ValueError("Endpoint not found")

    def delete_endpoint(self, name):
        with self._conn() as c:
            c.execute("DELETE FROM endpoints WHERE name = ?", (name,))



    # ---------- PERMISSIONS ----------

    def list_permissions(self):
        with self._conn() as c:
            rows = c.execute("""
                             SELECT p.uid AS permission_uid,
                                    p.active,
                                    ps.subject_type,
                                    ps.subject_id,
                                    pa.endpoint_name,
                                    pa.action
                             FROM permissions p
                                      LEFT JOIN permission_subjects ps
                                                ON ps.permission_uid = p.uid
                                      LEFT JOIN permission_actions pa
                                                ON pa.permission_uid = p.uid
                             ORDER BY p.uid
                             """).fetchall()

            permissions = {}

            for row in rows:
                pid = row["permission_uid"]

                if pid not in permissions:
                    permissions[pid] = {
                        "uid": pid,
                        "active": bool(row["active"]),
                        "subjects": [],
                        "endpoints": {}
                    }

                # sujetos
                if row["subject_type"] and row["subject_id"]:
                    subj = {
                        "type": row["subject_type"],
                        "id": row["subject_id"]
                    }
                    if subj not in permissions[pid]["subjects"]:
                        permissions[pid]["subjects"].append(subj)

                # endpoints + acciones
                if row["endpoint_name"] and row["action"]:
                    ep = permissions[pid]["endpoints"].setdefault(
                        row["endpoint_name"], []
                    )
                    if row["action"] not in ep:
                        ep.append(row["action"])

            # normalizar endpoints
            for perm in permissions.values():
                perm["endpoints"] = [
                    {"name": name, "actions": actions}
                    for name, actions in perm["endpoints"].items()
                ]

            return list(permissions.values())

    def grant_permission(self, subjects, endpoints):
        """
        subjects = [
            {"type": "user", "id": "user1"},
            {"type": "group", "id": "admins"}
        ]

        endpoints = [
            {"name": "get_data_orders", "actions": ["read", "write"]}
        ]
        """
        with self._conn() as c:
            # 1️⃣ crear la regla
            cur = c.execute("""
                            INSERT INTO permissions (active)
                            VALUES (1)
                            """)
            permission_uid = cur.lastrowid

            # 2️⃣ asignar sujetos
            for subject in subjects:
                c.execute("""
                          INSERT INTO permission_subjects
                              (permission_uid, subject_type, subject_id)
                          VALUES (?, ?, ?)
                          """, (
                              permission_uid,
                              subject["type"],
                              subject["id"]
                          ))

            # 3️⃣ asignar endpoints + acciones
            for ep in endpoints:
                for action in ep["actions"]:
                    c.execute("""
                              INSERT INTO permission_actions
                                  (permission_uid, endpoint_name, action)
                              VALUES (?, ?, ?)
                              """, (
                                  permission_uid,
                                  ep["name"],
                                  action
                              ))

            return permission_uid


    def disable_permission(self, uid):
        with self._conn() as c:
            c.execute(
                "UPDATE permissions SET active=0 WHERE uid=?", (uid,)
            )

    def enable_disable_permission(self, uid, action):
        with self._conn() as c:
            cur = c.execute(
                "UPDATE permissions SET active=? WHERE uid=?",
                (action, uid)
            )
            if cur.rowcount == 0:
                raise ValueError("Permission not found")




    # ---------- CONFIG ----------
    # ---------- DIALECTS ----------

    def list_dialects(self):
        with self._conn() as c:
            rows = c.execute(
                "SELECT id, key, name, supported_versions, is_active FROM dialects"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_dialect(self, dialect_id):
        with self._conn() as c:
            row = c.execute(
                "SELECT * FROM dialects WHERE id = ?",
                (dialect_id,)
            ).fetchone()
            if not row:
                raise ValueError("Dialect not found")
            return dict(row)

    def create_dialect(self, id, key, name, supported_versions, is_active=True):
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO dialects (id, key, name, supported_versions, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (id, key, name, supported_versions, int(is_active))
            )

    def update_dialect(self, dialect_id, fields: dict):
        keys = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [dialect_id]

        with self._conn() as c:
            cur = c.execute(
                f"UPDATE dialects SET {keys} WHERE id = ?",
                values
            )
            if cur.rowcount == 0:
                raise ValueError("Dialect not found")

    def enable_disable_dialect(self, dialect_id, action: int):
        self.update_dialect(dialect_id, {"is_active": action})


    # ---------- DATA SOURCES ----------

    def list_data_sources(self):
        with self._conn() as c:
            rows = c.execute(
                """
                SELECT ds.id,
                       ds.name,
                       ds.dialect_id,
                       d.key AS dialect_key,
                       d.name AS dialect_name,
                       ds.host,
                       ds.port,
                       ds.username,
                       ds.database_name,
                       ds.is_active
                FROM data_sources ds
                JOIN dialects d ON d.id = ds.dialect_id
                """
            ).fetchall()
            return [dict(r) for r in rows]

    def get_data_source(self, data_source_id):
        with self._conn() as c:
            row = c.execute(
                """SELECT 
                        ds.name,
                        ds.host,
                        ds.port,
                        ds.username,
                        ds.password,
                        ds.database_name,
                        d.key AS dialect
                        FROM data_sources ds 
                        JOIN dialects d ON d.id = ds.dialect_id
                        WHERE ds.id = ? """,
                (data_source_id,)
            ).fetchone()
            if not row:
                raise ValueError("Data source not found")
            return dict(row)


    def get_enabled_data_sources_for_runtime(self):
        """
        Devuelve las data sources activas en un formato
        consumible directamente por DbPoolManager.
        """
        with self._conn() as c:
            rows = c.execute("""
                SELECT
                    ds.id,
                    ds.name,
                    ds.host,
                    ds.port,
                    ds.username,
                    ds.password,
                    ds.database_name,
                    d.key AS dialect
                FROM data_sources ds
                JOIN dialects d ON d.id = ds.dialect_id
                WHERE ds.is_active = 1
                  AND d.is_active = 1
            """).fetchall()

            result = []

            for r in rows:
                result.append({
                    "name": r["name"],  # key lógico del pool
                    "dialect": r["dialect"],
                    "connection": {
                        "host": r["host"],
                        "port": r["port"],
                        "user": r["username"],
                        "pass": r["password"],
                        "database": r["database_name"],
                    }
                })

            return result


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
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO data_sources (
                    id, name, dialect_id, host, port,
                    username, password, database_name, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id, name, dialect_id, host, port,
                    username, password, database_name, int(is_active)
                )
            )

    def update_data_source(self, data_source_id, fields: dict):
        keys = ", ".join(f"{k}=?" for k in fields)
        values = list(fields.values()) + [data_source_id]

        with self._conn() as c:
            cur = c.execute(
                f"UPDATE data_sources SET {keys} WHERE id = ?",
                values
            )
            if cur.rowcount == 0:
                raise ValueError("Data source not found")

    def delete_data_source(self, data_source_id):
        with self._conn() as c:
            cur = c.execute(
                "DELETE FROM data_sources WHERE id = ?",
                (data_source_id,)
            )
            return cur.rowcount > 0


    # ---------- OBJECTS ----------

    def list_objects(self):
        with self._conn() as c:
            rows = c.execute(
                "select object, display_name, active from db_objects where active > 0"
            ).fetchall()
            return [dict(r) for r in rows]
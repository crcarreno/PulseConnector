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
                             SELECT DISTINCT pa.endpoint_name,
                                             pa.action
                             FROM permissions p
                                      INNER JOIN permission_actions pa
                                                 ON pa.permission_uid = p.uid
                                      LEFT JOIN group_users gu
                                                ON p.by_type = 'group'
                                                    AND gu.group_name = p.target
                             WHERE p.active = 1
                               AND (
                                 (p.by_type = 'user' AND p.target = ?)
                                     OR (p.by_type = 'group' AND gu.user = ?)
                                 )
                             """, (username, username)).fetchall()

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
            return c.execute("SELECT * FROM endpoints").fetchall()

    def register_endpoint(self, ep: dict):
        with self._conn() as c:
            c.execute("""
                INSERT INTO endpoints
                (name, dialect, database_name, type, source, namespace, primary_key)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ep["name"], ep["dialect"], ep["database"],
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
            return c.execute("SELECT * FROM permissions").fetchall()


    def grant_permission(self, by_type, target, endpoints):
        with self._conn() as c:
            cur = c.execute("""
                INSERT INTO permissions (by_type, target)
                VALUES (?, ?)
            """, (by_type, target))
            uid = cur.lastrowid

            for ep in endpoints:
                for action in ep["actions"]:
                    c.execute("""
                        INSERT INTO permission_actions
                        (permission_uid, endpoint_name, action)
                        VALUES (?, ?, ?)
                    """, (uid, ep["name"], action))
            return uid


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

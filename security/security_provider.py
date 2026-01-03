import json
from pathlib import Path
from typing import Dict, Any


class SecurityProvider:

    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)

        self._users = {}
        self._groups = {}
        self._endpoints = {}
        self._permissions = {}
        self._masterPass = {}

        self.load_all()

    # -------------------------
    # Carga inicial
    # -------------------------

    def load_all(self):
        self._users = self._load_file("users.json").get("users", [])
        self._groups = self._load_file("groups.json").get("groups", [])
        self._endpoints = self._load_file("endpoints.json").get("endpoints", [])
        perms = self._load_file("permissions.json")
        self._permissions = perms.get("permissions", [])
        self._priority = perms.get("priority", "user_over_group")

    def _load_file(self, filename: str) -> Dict[str, Any]:
        path = self.config_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_file(self, filename: str, data: Dict[str, Any]):
        path = self.config_dir / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # -------------------------
    # Getters
    # -------------------------

    def get_users(self):
        return self._users

    def get_groups(self):
        return self._groups

    def get_endpoints(self):
        return self._endpoints

    def get_permissions(self):
        return self._permissions

    def get_priority(self):
        return self._priority

    def get_master_password(self):
        return self._masterPass

    # -------------------------
    # Lookups útiles
    # -------------------------

    def get_user(self, username: str):
        return next((u for u in self._users if u["user"] == username), None)

    def get_group(self, group_name: str):
        return next((g for g in self._groups if g["group"] == group_name), None)

    def get_endpoint(self, name: str):
        return next((e for e in self._endpoints if e["name"] == name), None)

    # -------------------------
    # Escritura / updates
    # -------------------------

    def save_users(self):
        self._write_file("users.json", {"users": self._users})

    def save_groups(self):
        self._write_file("groups.json", {"groups": self._groups})

    def save_endpoints(self):
        self._write_file("endpoints.json", {"endpoints": self._endpoints})

    def save_permissions(self):
        self._write_file(
            "permissions.json",
            {
                "permissions": self._permissions,
                "priority": self._priority
            }
        )

    def reload(self):
        """Recarga todos los archivos desde disco"""
        self._load_all()


    def is_allowed(self, username, endpoint_name, action):

        # permisos directos al usuario
        user_perms = [
            p for p in self.permissions
            if p["by"] == "user"
               and username in p["group_or_user"]
               and p["active"]
        ]

        # permisos por grupo
        groups = self.get_user_groups(username)

        group_perms = [
            p for p in self.permissions
            if p["by"] == "group"
               and any(g in p["group_or_user"] for g in groups)
               and p["active"]
        ]

        perms = user_perms + group_perms

        for perm in perms:
            for ep in perm["endpoints"]:
                if ep["name"] == endpoint_name and action in ep["actions"]:
                    return True

        return False


    def get_user_groups(self, username):
        return [
            g["group"]
            for g in self.groups
            if username in g.get("users", [])
        ]

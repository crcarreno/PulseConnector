
from security.storage.sqlite_storage import SQLiteStorage

class IAMService:

    def __init__(self, storage: SQLiteStorage):
        self.db = storage

    # USERS
    def validate_user(self, user, password_hash):
        return self.db.validate_user_credentials(user, password_hash)

    def list_users(self):
        return [dict(u) for u in self.db.list_users()]

    def get_user(self, user):
        return dict(self.db.get_user(user))

    def create_user(self, user, display, password):
        self.db.create_user(user, display, password)

    def update_user(self, user, fields):
        self.db.update_user(user, fields)

    def enable_disable_user(self, user, action):
        self.db.enable_disable_user(user, action)


    # GROUPS
    def list_groups(self):
        return [dict(g) for g in self.db.list_groups()]

    def create_group(self, group, display):
        self.db.create_group(group, display)

    def add_user_to_group(self, group, user):
        self.db.add_user_to_group(group, user)

    def remove_user_from_group(self, group, user):
        self.db.remove_user_from_group(group, user)

    def disable_group(self, group):
        self.db.disable_group(group)

    def get_group(self, group):
        groups = self.db.list_groups()
        for g in groups:
            if g["group_name"] == group:
                return dict(g)
        raise ValueError("Group not found")

    def update_group(self, group, fields):
        self.db.update_group(group, fields)

    def enable_disable_group(self, group, action):
        self.db.enable_disable_group(group, action)

    def list_group_members(self, group):
        return self.db.list_group_members(group)


    # ENDPOINTS
    def list_endpoints(self):
        return [dict(e) for e in self.db.list_endpoints()]

    def register_endpoint(self, ep):
        self.db.register_endpoint(ep)

    def update_endpoint(self, name, fields):
        self.db.update_endpoint(name, fields)

    def delete_endpoint(self, name):
        self.db.delete_endpoint(name)

    def get_endpoint(self, name):
        endpoints = self.db.list_endpoints()
        for e in endpoints:
            if e["name"] == name:
                return dict(e)
        raise ValueError("Endpoint not found")

    # PERMISSIONS
    def list_permissions(self):
        # ya viene estructurado desde db
        return self.db.list_permissions()

    def grant_permission(self, subjects, endpoints):
        """
        subjects = [
            {"type": "user", "id": "user1"},
            {"type": "group", "id": "admins"}
        ]
        """
        if not subjects:
            raise ValueError("At least one subject is required")

        if not endpoints:
            raise ValueError("At least one endpoint is required")

        return self.db.grant_permission(subjects, endpoints)

    def update_permission(self, uid, subjects, endpoints):
        if not subjects:
            raise ValueError("At least one subject is required")

        if not endpoints:
            raise ValueError("At least one endpoint is required")

        self.db.update_permission(uid, subjects, endpoints)

    def disable_permission(self, uid):
        self.db.disable_permission(uid)

    def get_permission(self, uid):
        perms = self.db.list_permissions()
        for p in perms:
            if p["uid"] == uid:
                return dict(p)
        raise ValueError("Permission not found")

    def enable_disable_permission(self, uid, action):
        self.db.enable_disable_permission(uid, action)


    # OBJECTS
    def list_objects(self):
        return [dict(o) for o in self.db.list_objects()]
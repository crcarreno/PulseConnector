
from uuid import uuid4
from flask import request, current_app
from database.db_config import config_db
from security.config_services import ConfigServices
from security.iam_services import IAMService
from security.password_hasher import PasswordHasher
from security.storage.schemas import SchemaExtractorFactory
from utils.api_response import api_response

from . import api_bp

iam = IAMService(config_db)
conf = ConfigServices()


# ------------- Objects ----------------
@api_bp.get("/admin/objects")
def list_objects():
    return api_response(data=iam.list_objects())


@api_bp.post("/admin/schema/objects")
def list_schema_objects_endpoint():
    data = request.get_json(silent=True)

    if not data:
        return api_response(False, error="Request body is required", status=400)

    connection_id = data.get("connection_id")
    object_type = data.get("object_type")

    if not connection_id or not object_type:
        return api_response(
            False,
            error="connection_id and object_type are required",
            status=400
        )

    conf_connection = current_app.config_db.get_data_source(connection_id)
    if conf_connection is None:
        return api_response(False, error="Connection not found", status=404)

    #db = current_app.db_pools.get_db(conf_connection["name"])

    db_pool = current_app.config["DB_POOL_MANAGER"]
    db = db_pool.get_db(conf_connection["name"])

    extractor = SchemaExtractorFactory.create(db)

    if object_type == "table":
        items = extractor.get_tables()
    elif object_type == "view":
        items = extractor.get_views()
    elif object_type in ("sp", "stored_procedure"):
        items = extractor.get_stored_procedures()
    else:
        return api_response(
            False,
            error=f"Unsupported object type: {object_type}",
            status=400
        )

    return api_response(data={
        "items": items,
        "count": len(items)
    })


# ------------- Dialects ----------------
@api_bp.get("/admin/dialects")
def list_dialects_endpoint():
    dialects = conf.list_dialects()
    return api_response(data={
        "items": dialects,
        "count": len(dialects)
    })


@api_bp.post("/admin/dialects")
def create_dialect_endpoint():
    data = request.get_json(silent=True)

    if not data:
        return api_response(False, error="Request body is required", status=400)

    key = data.get("key")
    name = data.get("name")
    versions = data.get("supported_versions")

    if not key or not name or not versions:
        return api_response(
            False,
            error="key, name and supported_versions are required",
            status=400
        )

    conf.create_dialect(
        id=str(uuid4()),
        key=key,
        name=name,
        supported_versions=versions,
        is_active=data.get("is_active", True)
    )

    return api_response(data={"status": "created"}, status=201)


# ------------- Data Sources ----------------
@api_bp.get("/admin/data-sources")
def list_data_sources_endpoint():
    data_sources = conf.list_data_sources()
    return api_response(data={
        "items": data_sources,
        "count": len(data_sources)
    })


@api_bp.post("/admin/data-sources")
def create_data_source_endpoint():
    data = request.get_json(silent=True)

    if not data:
        return api_response(False, error="Request body is required", status=400)

    required_fields = [
        "name", "dialect_id", "host", "port",
        "username", "password", "database_name"
    ]

    for field in required_fields:
        if not data.get(field):
            return api_response(False, error=f"{field} is required", status=400)

    conf.create_data_source(
        id=str(uuid4()),
        name=data["name"],
        dialect_id=data["dialect_id"],
        host=data["host"],
        port=data["port"],
        username=data["username"],
        password=data["password"],
        database_name=data["database_name"],
        is_active=data.get("is_active", True)
    )

    return api_response(data={"status": "created"}, status=201)


@api_bp.put("/admin/data-sources/<data_source_id>")
def update_data_source_endpoint(data_source_id):
    data = request.get_json(silent=True)

    if not data:
        return api_response(False, error="Request body is required", status=400)

    updated = conf.update_data_source(data_source_id, **data)

    if not updated:
        return api_response(False, error="Data source not found", status=404)

    return api_response(data={"status": "updated"})


@api_bp.delete("/admin/data-sources/<data_source_id>")
def delete_data_source_endpoint(data_source_id):
    deleted = conf.delete_data_source(data_source_id)

    if not deleted:
        return api_response(False, error="Data source not found", status=404)

    return api_response(data={"status": "deleted"})


# ------------- Users ----------------
@api_bp.post("/admin/users")
def create_user_endpoint():
    data = request.get_json(silent=True)

    if not data:
        return api_response(False, error="Request body is required", status=400)

    user = data.get("user")
    password = data.get("password_hash")

    if not user or not password:
        return api_response(False, error="user and password are required", status=400)

    ph = PasswordHasher()

    iam.create_user(
        user=user,
        display=data.get("display_name", ""),
        password=ph.hash_password(password)
    )

    return api_response(data={"status": "created"}, status=201)


@api_bp.get("/admin/users")
def list_users():
    return api_response(data=iam.list_users())


@api_bp.post("/admin/users/get")
def get_user():
    data = request.get_json(silent=True)
    return api_response(data=iam.get_user(data["user"]))


@api_bp.post("/admin/users/update")
def update_user():
    data = request.get_json(silent=True)

    user = data.get("user")
    fields = {}

    if "display_name" in data:
        fields["display_name"] = data["display_name"]

    if "password_hash" in data:
        ph = PasswordHasher()
        fields["password_hash"] = ph.hash_password(data["password_hash"])

    if not fields:
        return api_response(False, error="No fields to update", status=400)

    iam.update_user(user, fields)
    return api_response(data={"status": "updated"})


@api_bp.post("/admin/users/disable")
def enable_disable_user():
    data = request.get_json(silent=True)

    iam.enable_disable_user(data["user"], data["action"])

    status = "enabled" if data["action"] == 1 else "disabled"
    return api_response(data={"status": status})


# ------------- Groups ----------------
@api_bp.post("/admin/groups")
def create_group_endpoint():
    data = request.get_json(silent=True)

    iam.create_group(
        group=data["group"],
        display=data.get("display_name", "")
    )

    return api_response(data={"status": "created"}, status=201)


@api_bp.get("/admin/groups")
def list_groups():
    return api_response(data=iam.list_groups())


@api_bp.post("/admin/groups/get")
def get_group():
    data = request.get_json(silent=True)
    return api_response(data=iam.get_group(data["group"]))


@api_bp.post("/admin/groups/update")
def update_group():
    data = request.get_json(silent=True)

    fields = {}
    if "display_name" in data:
        fields["display_name"] = data["display_name"]

    if not fields:
        return api_response(False, error="No fields to update", status=400)

    iam.update_group(data["group"], fields)
    return api_response(data={"status": "updated"})


@api_bp.post("/admin/groups/disable")
def enable_disable_group():
    data = request.get_json(silent=True)

    iam.enable_disable_group(data["group"], data["action"])
    status = "enabled" if data["action"] == 1 else "disabled"

    return api_response(data={"status": status})


@api_bp.post("/admin/groups/add-user")
def add_user_to_group():
    data = request.get_json(silent=True)

    iam.add_user_to_group(data["group"], data["user"])
    return api_response(data={"status": "user added"}, status=201)


@api_bp.post("/admin/groups/remove-user")
def remove_user_from_group():
    data = request.get_json(silent=True)

    iam.remove_user_from_group(data["group"], data["user"])
    return api_response(data={"status": "user removed"})


@api_bp.post("/admin/groups/members")
def list_group_members():
    data = request.get_json(silent=True)
    return api_response(data=iam.list_group_members(data["group"]))


# ------------- Endpoints ----------------
@api_bp.post("/admin/endpoints")
def create_endpoint_endpoint():
    data = request.get_json(silent=True)

    iam.register_endpoint({
        "name": data["name"],
        "id_connection": data["id_connection"],
        "type": data["type"],
        "source": data["source"],
        "namespace": data["namespace"],
        "primary_key": data.get("primary_key", "")
    })

    return api_response(data={"status": "created"}, status=201)


@api_bp.get("/admin/endpoints")
def list_endpoints():
    return api_response(data=iam.list_endpoints())


@api_bp.post("/admin/endpoints/get")
def get_endpoint():
    data = request.get_json(silent=True)
    return api_response(data=iam.get_endpoint(data["name"]))


@api_bp.post("/admin/endpoints/update")
def update_endpoint():
    data = request.get_json(silent=True)

    fields = {
        k: data[k]
        for k in ["dialect", "database", "type", "source", "namespace", "primary_key"]
        if k in data
    }

    if not fields:
        return api_response(False, error="No fields to update", status=400)

    iam.update_endpoint(data["name"], fields)
    return api_response(data={"status": "updated"})


# ------------- Permissions ----------------
@api_bp.post("/admin/permissions")
def create_permission():
    data = request.get_json(silent=True)

    uid = iam.grant_permission(
        subjects=data["subjects"],
        endpoints=data["endpoints"]
    )

    return api_response(data={"status": "created", "uid": uid}, status=201)


@api_bp.get("/admin/permissions")
def list_permissions():
    return api_response(data=iam.list_permissions())


@api_bp.post("/admin/permissions/get")
def get_permission():
    data = request.get_json(silent=True)
    return api_response(data=iam.get_permission(data["uid"]))


@api_bp.post("/admin/permissions/disable")
def enable_disable_permission():
    data = request.get_json(silent=True)

    iam.enable_disable_permission(data["uid"], data["action"])
    status = "enabled" if data["action"] == 1 else "disabled"

    return api_response(data={"status": status})

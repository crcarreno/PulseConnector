from uuid import uuid4

from routes.api_routes import app
from flask import render_template, request, abort
from security.iam_services import IAMService
from security.config_services import ConfigServices
from security.password_hasher import PasswordHasher

iam = IAMService()
conf = ConfigServices()

# ------------- Views -----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/index")
def index():
    return render_template("index.html")



# ------------- Config ---------------
# ------------- Dialects -------------
@app.get("/admin/dialects")
def list_dialects_endpoint():
    dialects = conf.list_dialects()

    return {
        "items": dialects,
        "count": len(dialects)
    }

@app.post("/admin/dialects")
def create_dialect_endpoint():
    data = request.get_json(silent=True)

    if not data:
        abort(400, description="Request body is required")

    key = data.get("key")
    name = data.get("name")
    versions = data.get("supported_versions")

    if not key or not name or not versions:
        abort(400, description="key, name and supported_versions are required")

    conf.create_dialect(
        id=str(uuid4()),
        key=key,
        name=name,
        supported_versions=versions,
        is_active=data.get("is_active", True)
    )

    return {"status": "created"}, 201


# ---- Data Sources (DB Connections) ----
@app.get("/admin/data-sources")
def list_data_sources_endpoint():
    data_sources = conf.list_data_sources()

    return {
        "items": data_sources,
        "count": len(data_sources)
    }


@app.post("/admin/data-sources")
def create_data_source_endpoint():
    data = request.get_json(silent=True)

    if not data:
        abort(400, description="Request body is required")

    required_fields = [
        "name",
        "dialect_id",
        "host",
        "port",
        "username",
        "password",
        "database_name"
    ]

    for field in required_fields:
        if not data.get(field):
            abort(400, description=f"{field} is required")

    conf.create_data_source(
        id=str(uuid4()),
        name=data["name"],
        dialect_id=data["dialect_id"],
        host=data["host"],
        port=data["port"],
        username=data["username"],
        password=data["password"],  # encrypt before persist
        database_name=data["database_name"],
        is_active=data.get("is_active", True)
    )

    return {"status": "created"}, 201


@app.put("/admin/data-sources/<data_source_id>")
def update_data_source_endpoint(data_source_id):
    data = request.get_json(silent=True)

    if not data:
        abort(400, description="Request body is required")

    updated = conf.update_data_source(
        data_source_id,
        **data
    )

    if not updated:
        abort(404, description="Data source not found")

    return {"status": "updated"}


@app.delete("/admin/data-sources/<data_source_id>")
def delete_data_source_endpoint(data_source_id):
    deleted = conf.delete_data_source(data_source_id)

    if not deleted:
        abort(404, description="Data source not found")

    return {"status": "deleted"}




# ------------- User -----------------
# User create
@app.post("/admin/users")
def create_user_endpoint():

    data = request.get_json(silent=True)

    if not data:
        abort(400, description="Request body is required")

    user = data.get("user")
    password = data.get("password_hash")

    if not user or not password:
        abort(400, description="user and password are required")

    ph = PasswordHasher()

    iam.create_user(
        user=user,
        display=data.get("display_name", ""),
        password=ph.hash_password(password)
    )

    return {"status": "created"}, 201

# User list
@app.get("/admin/users")
def list_user():
    return iam.list_users()

# User get
@app.post("/admin/users/get")
def get_user():
    data = request.json
    return iam.get_user(data["user"]), 200

# User update
@app.post("/admin/users/update")
def update_user():
    data = request.json

    user = data["user"]
    fields = {}

    if "display_name" in data:
        fields["display_name"] = data["display_name"]

    ph = PasswordHasher()

    if "password_hash" in data:
        fields["password_hash"] = ph.hash_password(data["password_hash"])

    if not fields:
        return {"error": "No fields to update"}, 400

    iam.update_user(user, fields)
    return {"status": "updated"}, 200

# User disable
@app.post("/admin/users/disable")
def enable_disable_user():
    data = request.json
    iam.enable_disable_user(data["user"], data["action"])

    if data["action"] == 1:
        return {"status": "enabled"}, 201
    else:
        return {"status": "disabled"}, 200


# ------------- Groups -----------------
# Group create
@app.post("/admin/groups")
def create_group_endpoint():
    data = request.json

    iam.create_group(
        group=data["group"],
        display=data.get("display_name", "")
    )

    return {"status": "created"}, 201

# Group list
@app.get("/admin/groups")
def list_groups():
    return iam.list_groups(), 200

# Group get
@app.post("/admin/groups/get")
def get_group():
    data = request.json
    return iam.get_group(data["group"]), 200

# Group update
@app.post("/admin/groups/update")
def update_group():
    data = request.json

    group = data["group"]
    fields = {}

    if "display_name" in data:
        fields["display_name"] = data["display_name"]

    if not fields:
        return {"error": "No fields to update"}, 400

    iam.update_group(group, fields)
    return {"status": "updated"}, 200

# Group disable
@app.post("/admin/groups/disable")
def enable_disable_group():
    data = request.json

    iam.enable_disable_group(
        group=data["group"],
        action=data["action"]
    )

    if data["action"] == 1:
        return {"status": "enabled"}, 201
    else:
        return {"status": "disabled"}, 200

# Group add user
@app.post("/admin/groups/add-user")
def add_user_to_group():
    data = request.json

    iam.add_user_to_group(
        group=data["group"],
        user=data["user"]
    )

    return {"status": "user added"}, 201

# Group remove user
@app.post("/admin/groups/remove-user")
def remove_user_from_group():
    data = request.json

    iam.remove_user_from_group(
        group=data["group"],
        user=data["user"]
    )

    return {"status": "user removed"}, 200

# Group list members
@app.post("/admin/groups/members")
def list_group_members():
    data = request.json
    return iam.list_group_members(data["group"]), 200


# ------------- Endpoint -----------------
# Endpoint create
@app.post("/admin/endpoints")
def create_endpoint_endpoint():
    data = request.json

    iam.register_endpoint({
        "name": data["name"],
        "dialect": data["dialect"],
        "database": data["database"],
        "type": data["type"],
        "source": data["source"],
        "namespace": data["namespace"],
        "primary_key": data.get("primary_key", "")
    })

    return {"status": "created"}, 201

# Endpoint list
@app.get("/admin/endpoints")
def list_endpoints():
    return iam.list_endpoints(), 200

# Endpoint get
@app.post("/admin/endpoints/get")
def get_endpoint():
    data = request.json
    return iam.get_endpoint(data["name"]), 200

# Endpoint update
@app.post("/admin/endpoints/update")
def update_endpoint():
    data = request.json

    name = data["name"]
    fields = {}

    for key in ["dialect", "database", "type", "source", "namespace", "primary_key"]:
        if key in data:
            fields[key] = data[key]

    if not fields:
        return {"error": "No fields to update"}, 400

    iam.update_endpoint(name, fields)
    return {"status": "updated"}, 200


# ------------- Permissions -----------------
# Permissions create
@app.post("/admin/permissions")
def create_permission():
    data = request.json

    uid = iam.grant_permission(
        by=data["by"],                 # 'user' | 'group'
        target=data["target"],         # user o group
        endpoints=data["endpoints"]    # lista de endpoints + actions
    )

    return {"status": "created", "uid": uid}, 201

# Permissions list
@app.get("/admin/permissions")
def list_permissions():
    return iam.list_permissions(), 200

# Permissions get
@app.post("/admin/permissions/get")
def get_permission():
    data = request.json
    return iam.get_permission(data["uid"]), 200

# Permissions disable
@app.post("/admin/permissions/disable")
def enable_disable_permission():
    data = request.json

    iam.enable_disable_permission(
        uid=data["uid"],
        action=data["action"]
    )

    if data["action"] == 1:
        return {"status": "enabled"}, 201
    else:
        return {"status": "disabled"}, 200

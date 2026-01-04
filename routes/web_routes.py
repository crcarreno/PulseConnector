from routes.api_routes import app
from flask import render_template, request
from security.iam_services import IAMService

iam = IAMService()

# ------------- Front-end -----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/index")
def index():
    return render_template("index.html")


# ------------- Back-end -----------------
# ------------- User -----------------
# User create
@app.post("/admin/users")
def create_user_endpoint():
    data = request.json

    iam.create_user(
        user=data["user"],
        display=data.get("display_name", ""),
        password=data["password_hash"]
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

    if "password_hash" in data:
        fields["password_hash"] = data["password_hash"]

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

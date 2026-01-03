from collections import defaultdict

from flask import Flask, request, jsonify, abort, json

from analytics.usage_counter import increment_request
from db import DB
from security.password_hasher import PasswordHasher
from security.security_provider import SecurityProvider
from threads import server_state
from threads.log_bridge import log_bridge
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from utils import CONFIG_PATH, SECURITY_PATH
from version import __version__
from analytics.logger import setup_logger

log = setup_logger()

app = Flask(__name__)
db = None

basic_auth = HTTPBasicAuth()

with open(CONFIG_PATH) as f:
    cfg = json.load(f)
    secure_cfg = cfg["security"]

app.config["JWT_SECRET_KEY"] = secure_cfg["jwt_secret_key"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=secure_cfg["jwt_access_token_expires"])
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=secure_cfg["jwt_refresh_token_expires"])

admin_user = secure_cfg["admin_user"]

jwt = JWTManager(app)


secProvider = SecurityProvider(SECURITY_PATH)
secProvider.load_all()

users = secProvider.get_users()
groups = secProvider.get_groups()
endpoints = secProvider.get_endpoints()
permissions = secProvider.get_permissions()

USER_PERMISSIONS = defaultdict(lambda: defaultdict(set))

def build_permission_cache():

    for perm in permissions:
        if not perm["active"]:
            continue

        targets = perm["group_or_user"]

        for ep in perm["endpoints"]:
            ep_name = ep["name"]
            actions = set(ep["actions"])

            if perm["by"] == "user":
                for user in targets:
                    USER_PERMISSIONS[user][ep_name].update(actions)

            elif perm["by"] == "group":
                for group in targets:
                    grp = secProvider.get_group(group)
                    if not grp:
                        continue
                    for user in grp.get("users", []):
                        USER_PERMISSIONS[user][ep_name].update(actions)


build_permission_cache()

ENDPOINT_BY_NAMESPACE = {}

for ep in endpoints:
    namespace = ep.get("namespace")
    name = ep.get("name")

    if not namespace or not name:
        continue

    ENDPOINT_BY_NAMESPACE.setdefault(namespace, {})[name] = ep


def reload_security():
    USER_PERMISSIONS.clear()
    secProvider.load_all()
    build_permission_cache()


def init_db(cfg, analytics):
    global db
    db = DB(cfg, analytics)

'''
    BASIC AUTH
'''
@basic_auth.verify_password
def verify_basic(username, password):

    if username == admin_user:
        return {"username": username, "status": "allow"}

    return {"username": "No status", "status": "deny"}


@app.route("/version")
def get_version():
    return {"version": __version__}


@app.route("/status")
@basic_auth.login_required
def health():
    return {"status": "ok", "version": __version__, "user": basic_auth.current_user()}

'''
    JWT AUTH
'''
@app.route("/login", methods=["POST"])
def login():
    try:

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"msg": "Username and password required"}, 400

        user = secProvider.get_user(username)

        if not user or not user.get("active"):
            return {"msg": "Invalid credentials"}, 401

        #hasher = PasswordHasher()

        #if not hasher.verify_password(user["password_hash"], password):
        #    return {"msg": "Invalid credentials"}, 401

        access_token = create_access_token(
            identity=username
        )

        return {"access_token": access_token}

    except Exception as e:
        log.error(f"Login error: {e}")
        return {"error": "Internal error"}, 500


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "token_expired",
        "msg": "El token ha expirado"
    }), 401


@app.before_request
def guard():

    if request.path in ("/status", "/version"):
        return

    if not server_state.running:
        abort(503, "Server stopped")


@app.before_request
def log_request():

    try:
        payload = {
            "type": "request",
            "method": request.method,
            "path": request.path + str(request.args.to_dict(flat=True)),
            "remote": request.remote_addr,
            "args": request.args.to_dict()
        }

        log_bridge.log.emit(json.dumps(payload))

    except Exception as e:
        log.error("Error: {}".format(e))
        return jsonify({"error": str(e)}), 500


def can_access(username, endpoint_name, action):
    return action in USER_PERMISSIONS.get(username, {}).get(endpoint_name, ())


@app.route("/odata/<namespace>/<endpoint_name>", methods=["GET"])
@jwt_required()
def odata_table(namespace, endpoint_name):

    endpoint = ENDPOINT_BY_NAMESPACE.get(namespace, {}).get(endpoint_name)

    if not endpoint:
        abort(404, "Endpoint not found")

    username = get_jwt_identity()

    if not can_access(username, endpoint_name, "read"):
        abort(403, "Permission denied")

    table_name = endpoint["source"]

    args = request.args
    params = {
        k: args[k]
        for k in ("$select", "$filter", "$top", "$skip", "$orderby")
        if k in args
    }

    try:
        result = db.query_odata(table_name, params)

        rows = result.get("rows", [])
        columns = result.get("columns", [])

        increment_request(
            kind="light" if len(rows) < 101 else "heavy",
            success=True
        )

        return jsonify([
            dict(zip(columns, row))
            for row in rows
        ])

    except Exception as e:
        log.error(f"OData error [{namespace}/{endpoint_name}]: {e}")
        increment_request(kind="light", success=False)
        return jsonify({"error": "Query execution failed"}), 500


@app.route("/odata/<namespace>/<endpoint_name>", methods=["POST"])
@jwt_required()
def odata_insert(namespace, endpoint_name):

    endpoint = ENDPOINT_BY_NAMESPACE.get(namespace, {}).get(endpoint_name)
    if not endpoint:
        abort(404, "Endpoint not found")

    username = get_jwt_identity()

    if not can_access(username, endpoint_name, "write"):
        abort(403, "Permission denied")

    table_name = endpoint["source"]

    try:
        body = request.get_json()
        if not body:
            abort(400, "json body required")

        result = db.insert_odata(table_name, body)
        return jsonify(result)

    except Exception as e:
        log.error(f"OData INSERT error [{namespace}/{endpoint_name}]: {e}")
        return jsonify({"error": "Insert failed"}), 500



@app.route("/odata/<namespace>/<endpoint_name>/<id>", methods=["PATCH", "PUT"])
@jwt_required()
def odata_update(namespace, endpoint_name, id):
    """
    PUT   -> replace all
    PATCH -> partial update
    """

    endpoint = ENDPOINT_BY_NAMESPACE.get(namespace, {}).get(endpoint_name)
    if not endpoint:
        abort(404, "Endpoint not found")

    username = get_jwt_identity()

    if not can_access(username, endpoint_name, "write"):
        abort(403, "Permission denied")

    table_name = endpoint["source"]

    try:
        body = request.get_json()
        if not body:
            abort(400, "json body required")

        result = db.update_odata(
            table_name = table_name,
            pk_name = endpoint.get("primary_key", "id"),
            pk_value = id,
            data = body
        )

        return jsonify(result)

    except Exception as e:
        log.error(f"OData UPDATE error [{namespace}/{endpoint_name}/{id}]: {e}")
        return jsonify({"error": "Update failed"}), 500

import routes.web_routes
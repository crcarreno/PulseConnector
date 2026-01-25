
from collections import defaultdict
from flask import request, jsonify
from analytics.logger import setup_logger
from analytics.usage_counter import increment_request
from flask_jwt_extended import jwt_required, get_jwt_identity

from db import DB
from security.iam_services import IAMService
from api import api_bp

iam = IAMService()
log = setup_logger()

USER_PERMISSIONS = defaultdict(lambda: defaultdict(set))
ENDPOINT_BY_NAMESPACE = {}
db = None


# ---------- Security cache ----------
def build_permission_cache(iam):
    USER_PERMISSIONS.clear()
    users = iam.list_users()
    for u in users:
        perms = iam.db.get_user_permissions(u["user"])
        for ep, actions in perms.items():
            USER_PERMISSIONS[u["user"]][ep].update(actions)


def reload_security():
    USER_PERMISSIONS.clear()
    build_permission_cache(iam)


def can_access(username, endpoint_name, action):
    return action in USER_PERMISSIONS.get(username, {}).get(endpoint_name, set())


# ---------- Endpoint cache ----------
def load_endpoints():
    ENDPOINT_BY_NAMESPACE.clear()
    for ep in iam.list_endpoints():
        namespace = ep["namespace"]
        name = ep["name"]
        ENDPOINT_BY_NAMESPACE.setdefault(namespace, {})[name] = ep


load_endpoints()


# ---------- DB ----------
def init_db(cfg, analytics):
    global db
    db = DB(cfg, analytics)


# ---------- OData ----------
@api_bp.route("/odata/<namespace>/<endpoint_name>", methods=["GET"])
@jwt_required()
def odata_table(namespace, endpoint_name):

    endpoint = ENDPOINT_BY_NAMESPACE.get(namespace, {}).get(endpoint_name)
    if not endpoint:
        return jsonify({"error": "Endpoint not found"}), 404

    username = get_jwt_identity()
    if not can_access(username, endpoint_name, "read"):
        return jsonify({"error": "Permission denied"}), 403

    args = request.args
    params = {
        k: args[k]
        for k in ("$select", "$filter", "$top", "$skip", "$orderby")
        if k in args
    }

    try:
        result = db.query_odata(endpoint["source"], params)

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


@api_bp.route("/odata/<namespace>/<endpoint_name>", methods=["POST"])
@jwt_required()
def odata_insert(namespace, endpoint_name):

    endpoint = ENDPOINT_BY_NAMESPACE.get(namespace, {}).get(endpoint_name)
    if not endpoint:
        return jsonify({"error": "Endpoint not found"}), 404

    username = get_jwt_identity()
    if not can_access(username, endpoint_name, "write"):
        return jsonify({"error": "Permission denied"}), 403

    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    try:
        result = db.insert_odata(endpoint["source"], body)
        return jsonify(result)

    except Exception as e:
        log.error(f"OData INSERT error [{namespace}/{endpoint_name}]: {e}")
        return jsonify({"error": "Insert failed"}), 500


@api_bp.route("/odata/<namespace>/<endpoint_name>/<id>", methods=["PATCH", "PUT"])
@jwt_required()
def odata_update(namespace, endpoint_name, id):

    endpoint = ENDPOINT_BY_NAMESPACE.get(namespace, {}).get(endpoint_name)
    if not endpoint:
        return jsonify({"error": "Endpoint not found"}), 404

    username = get_jwt_identity()
    if not can_access(username, endpoint_name, "write"):
        return jsonify({"error": "Permission denied"}), 403

    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    try:
        result = db.update_odata(
            table_name=endpoint["source"],
            pk_name=endpoint.get("primary_key", "id"),
            pk_value=id,
            data=body
        )
        return jsonify(result)

    except Exception as e:
        log.error(f"OData UPDATE error [{namespace}/{endpoint_name}/{id}]: {e}")
        return jsonify({"error": "Update failed"}), 500

from flask import Flask, request, jsonify, abort, json
from db import DB
from threads import server_state
from threads.log_bridge import log_bridge
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import timedelta
from utils import CONFIG_PATH
from version import __version__

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


def init_db(cfg):
    global db
    db = DB(cfg)

'''
    BASIC AUTH
'''
@basic_auth.verify_password
def verify_basic(username, password):

    if username == admin_user:
        return {"username": username, "status": "allow"}

    return {"username": "No status", "status": "deny"}


@app.route("/status")
@basic_auth.login_required
def health():
    return {"status": "ok", "version": __version__, "user": basic_auth.current_user()}

'''
    JWT AUTH
'''
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password or admin_user != password:
        return {"msg": "Invalid credentials"}, 401

    access_token = create_access_token(
        identity=username
    )

    return {
        "access_token": access_token
    }


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "token_expired",
        "msg": "El token ha expirado"
    }), 401


@app.before_request
def guard():
    # Permitimos siempre status
    if request.path == "/status":
        return

    # Si el server está "stopped", negamos servicio
    if not server_state.running:
        abort(503, "Server stopped")


@app.before_request
def log_request():
    payload = {
        "type": "request",
        "method": request.method,
        "path": request.path + str(request.args.to_dict(flat=True)),
        "remote": request.remote_addr,
        "args": request.args.to_dict()
    }
    log_bridge.log.emit(json.dumps(payload))


@app.route("/odata/<table_name>", methods=["GET"])
@jwt_required()
def odata_table(table_name):

    params = {}

    for k in request.args:
        if k in ("$select", "$filter", "$top", "$skip", "$orderby"):
            params[k] = request.args.get(k)
    try:

        result = db.query_odata(table_name, params)

        columns = result["columns"]
        rows = result["rows"]

        data = [
            dict(zip(columns, row))
            for row in rows
        ]

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/odata/<table_name>", methods=["POST"])
@jwt_required()
def odata_insert(table_name):

    body = request.json

    if not body:
        abort(400, "json body required")

    result = db.insert_odata(table_name, body)
    return jsonify(result)


@app.route("/odata/<table_name>/<id>", methods=["PATCH", "PUT"])
@jwt_required()
def odata_update(table_name, id):
    '''
        PUT: Replace all
        PATCH:  Replace only in json body
    '''
    body = request.json
    if not body:
        abort(400, "json body required")

    result = db.update_odata(table_name, "id", id, body)
    return jsonify(result)
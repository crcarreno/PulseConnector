from flask import Flask, request, jsonify, abort, json
from db import DB
from threads import server_state
from threads.log_bridge import log_bridge
from utils import CONFIG_PATH

app = Flask(__name__)
db = None


def init_db(cfg):
    global db
    db = DB(cfg)


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
def odata_table(table_name):

    params = {}

    for k in request.args:
        if k in ("$select", "$filter", "$top", "$skip", "$orderby"):
            params[k] = request.args.get(k)
    try:
        query = db.query_odata(table_name, params)
        conn = db.engine.connect()
        result = conn.execute(query)
        rows = [dict(r._mapping) for r in result.fetchall()]
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/odata/<table_name>", methods=["POST"])
def odata_insert(table_name):

    body = request.json

    if not body:
        abort(400, "json body required")

    result = db.insert_odata(table_name, body)
    return jsonify(result)


@app.route("/odata/<table_name>/<id>", methods=["PATCH", "PUT"])
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


@app.route("/status")
def status():
    return {"status": "ok"}

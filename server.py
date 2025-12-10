# server.py
from flask import Flask, request, jsonify, abort
from db import DB

app = Flask(__name__)
db = None
gui_logger = None

@app.before_request
def log_request():
    global gui_logger
    if gui_logger:
        gui_logger.log_bridge.log.emit(
            f"[REQ] {request.method} {request.path} {request.args.to_dict()}"
        )


def run_server(cfg, gui):
    global db, gui_logger
    db = DB(cfg)
    gui_logger = gui

    app.run(
        host=cfg["server"]["host"],
        port=cfg["server"]["port"],
        threaded=True
    )


@app.route("/odata/<table_name>", methods=["GET"])
def odata_table(table_name):
    params = {}
    # pasar solo parámetros OData ($select, $filter, $top, $skip, $orderby)
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

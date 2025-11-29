# server.py
from flask import Flask, request, jsonify, abort
from db import DB

app = Flask(__name__)
db = None

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

def run_server(cfg):
    global db
    db = DB(cfg)
    app.run(
        host=cfg["server"]["host"],
        port=cfg["server"]["port"],
        threaded=True
    )

@app.route("/__shutdown__", methods=["GET"])
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        return jsonify({"error": "No se puede apagar el servidor (no es Werkzeug)."}), 500
    func()
    return jsonify({"status": "ok", "msg": "Servidor apagándose..."})

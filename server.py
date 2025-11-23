# server.py
from flask import Flask, request, jsonify, abort
from db import DB
import threading, json

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

@app.route("/status")
def status():
    return {"status": "ok"}

def run_server(cfg):
    global db
    db = DB(cfg)
    app.run(host=cfg["server"]["host"], port=cfg["server"]["port"], threaded=True)

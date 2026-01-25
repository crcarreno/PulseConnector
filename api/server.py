
from flask import request, json
from analytics.logger import setup_logger
from threads import log_bridge
from threads.server_state import SERVER_STATE
from utils.api_response import api_response
from utils.version import __version__

from . import api_bp

log = setup_logger()


@api_bp.before_request
def before_request_pipeline():
    # guard (exclude health/version)
    if not request.path.endswith(("/status", "/version", "/health", "/start")):
        if not SERVER_STATE.get("running", False):
            return api_response(False, error="Server stopped", status=503)

    # logging
    try:
        payload = {
            "type": "request",
            "method": request.method,
            "path": request.path,
            "remote": request.remote_addr,
            "args": request.args.to_dict()
        }
        log_bridge.log.emit(json.dumps(payload))
    except Exception as e:
        log.error(e)


@api_bp.route("/server/start", methods=["POST"])
def start_server():
    if SERVER_STATE.get("running"):
        return api_response(False, error="Server already running", status=400)

    SERVER_STATE["running"] = True
    return api_response(data=SERVER_STATE)


@api_bp.route("/server/stop", methods=["POST"])
def stop_server():
    if not SERVER_STATE.get("running"):
        return api_response(False, error="Server not running", status=400)

    SERVER_STATE["running"] = False
    return api_response(data=SERVER_STATE)


@api_bp.route("/version", methods=["GET"])
def get_version():
    return api_response(data={"version": __version__})


# -------- Error handlers (API only) --------
@api_bp.errorhandler(404)
def not_found(e):
    return api_response(False, error="Not found", status=404)


@api_bp.errorhandler(403)
def forbidden(e):
    return api_response(False, error="Forbidden", status=403)


@api_bp.errorhandler(500)
def internal(e):
    log.error(e)
    return api_response(False, error="Internal server error", status=500)


from threads.server_state import SERVER_STATE
from utils.api_response import api_response
from . import api_bp


@api_bp.route("/health", methods=["GET"])
def health():
    return api_response(data={"status": "ok"})


@api_bp.route("/status", methods=["GET"])
def status():
    return api_response(data={
        "running": SERVER_STATE.get("running", False),
        "connections": SERVER_STATE.get("connections", 0),
    })

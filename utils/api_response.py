from flask import jsonify
from utils.version import __version__

def api_response(success=True, data=None, error=None, status=200):
    payload = {
        "success": success,
        "data": data,
        "error": error
    }

    return jsonify(payload), status

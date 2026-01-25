
from datetime import timedelta
from flask import Flask, json, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from analytics.analytics import Analytics
from analytics.logger import setup_logger
from threads.server_state import init_server_state
from security.config_services import load_config
from utils.utils import CONFIG_PATH
from bootstrap import run_bootstrap

from api import api_bp

log = setup_logger()

def create_app():

    run_bootstrap()

    app = Flask(__name__)

    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
        secure_cfg = cfg["security"]

    app.config["JWT_SECRET_KEY"] = secure_cfg["jwt_secret_key"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        minutes=secure_cfg["jwt_access_token_expires"]
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
        days=secure_cfg["jwt_refresh_token_expires"]
    )

    config = load_config()
    app.config.update(config)

    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "success": False,
            "data": None,
            "error": "token_expired"
        }), 401

    CORS(app, supports_credentials=True)

    init_server_state()

    app.register_blueprint(api_bp)

    return app


if __name__ == "__main__":

    try:
        analytics = Analytics()
        analytics.capture("api_start")
        analytics.send_daily_usage()

        log.info("Starting PulseConnector API")

        app = create_app()
        app.run(
            host=app.config.get("HOST", "0.0.0.0"),
            port=app.config.get("PORT", 5000),
            debug=app.config.get("DEBUG", False),
        )

    except Exception:
        log.exception("Fatal error starting API")
        raise

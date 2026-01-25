import threading
from datetime import timedelta
from flask import Flask, json, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from waitress import serve

from analytics.analytics import Analytics
from analytics.logger import setup_logger
from threads.server_state import init_server_state
from security.config_services import load_config
from utils.utils import CONFIG_PATH
from bootstrap import run_bootstrap

from api import api_bp
from security.proxy import start_https_proxy

log = setup_logger()


def create_app():
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

    #CORS(app, supports_credentials=True)

    init_server_state()
    app.register_blueprint(api_bp)

    return app

'''
def start_api():
    app = create_app()

    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
        server_cfg = cfg["server"]

    host = server_cfg["internal_host"]
    port = server_cfg["internal_port"]

    log.info(f"Starting internal API on http://{host}:{port}")

    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False
    )
'''

def start_api():
    app = create_app()

    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
        server_cfg = cfg["server"]

    host = server_cfg["internal_host"]
    port = server_cfg["internal_port"]

    log.info(
        f"Starting internal API with Waitress on "
        f"http://{host}:{port}"
    )

    serve(
        app,
        host = host,
        port = port,
        threads = server_cfg["threads"],
        connection_limit = server_cfg["connection_limit"],  # max connections concurrent
        backlog = server_cfg["backlog"],  # socket queue
        channel_timeout = server_cfg["channel_timeout"],  # kills hanging customers
        cleanup_interval = server_cfg["cleanup_interval"],  # kills dead connections
        expose_tracebacks = True  # útil en dev
    )


def main():
    try:
        log.info("Bootstrapping PulseConnector")
        run_bootstrap()

        analytics = Analytics()
        analytics.capture("api_start")
        analytics.send_daily_usage()

        # 1️⃣ API interna (Flask)
        threading.Thread(
            target=start_api,
            name="api-thread",
            daemon=True
        ).start()

        # 2️⃣ Proxy HTTPS (frontal, bloqueante)
        log.info("Starting HTTPS reverse proxy")
        start_https_proxy()

    except Exception:
        log.exception("Fatal error starting PulseConnector")
        raise


if __name__ == "__main__":
    main()

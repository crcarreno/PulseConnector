import json
import threading
from waitress import serve
from threads import server_state
from utils import CONFIG_PATH
from routes.api_routes import app, init_db
from threads.log_bridge import log_bridge
from proxy import start_https_proxy
from analytics.logger import setup_logger

log = setup_logger()


with open(CONFIG_PATH) as f:
    cfg = json.load(f)
    server_cfg = cfg["server"]


class ServerController:

    def __init__(self, cfg, analytics):
        self.analytics = analytics
        self.cfg = cfg
        self.thread = None
        self.proxy_thread = None
        self.analytics = analytics

    def start(self):

        try:
            self.analytics.capture("app_start_server")

            if self.thread and self.thread.is_alive():
                server_state.running = True
                log_bridge.log.emit(f"Server initialized internal in: http//:{server_cfg["internal_host"]}:{server_cfg["internal_port"]}")
                return

            log_bridge.log.emit(f"Server initialized internal in: http://{server_cfg["internal_host"]}:{server_cfg["internal_port"]}")

            init_db(self.cfg, self.analytics)
            server_state.running = True

            self.thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )

            self.thread.start()

            log_bridge.log.emit(f"HTTPS proxy initialized external in: https://{server_cfg["public_host"]}:{server_cfg["public_port"]}")

            self.proxy_thread = threading.Thread(
                target=start_https_proxy,
                args=(self.cfg["server"],),
                daemon=True
            )
            self.proxy_thread.start()

        except Exception as e:
            log.error("Error: {}".format(e))
            raise e


    def _run_server(self):

        try:
            serve(
                app,
                host=server_cfg["internal_host"],
                port=server_cfg["internal_port"],
                threads=server_cfg["threads"],
                connection_limit=server_cfg["connection_limit"],  # max connections concurrent
                backlog=server_cfg["backlog"],  # socket queue
                channel_timeout=server_cfg["channel_timeout"],  # kills hanging customers
                cleanup_interval=server_cfg["cleanup_interval"]  # kills dead connections
            )

        except Exception as e:
            log.error("Error: {}".format(e))
            raise e


    def stop(self):

        self.analytics.capture("app_stop_server")

        log_bridge.log.emit(f"Server stopped")
        server_state.running = False


    def restart(self):

        self.analytics.capture("app_restart_server")

        log_bridge.log.emit(f"Server restart")

        server_state.running = False
        server_state.running = True
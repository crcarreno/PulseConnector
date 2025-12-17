import json
import threading
from waitress import serve

from threads import server_state
from utils import resource_path
from web_route import app, init_db
from threads.log_bridge import log_bridge


with open(resource_path("config.json")) as f:
    cfg = json.load(f)
    server_cfg = cfg["server"]


class ServerController:

    def __init__(self, cfg):
        self.cfg = cfg
        self.thread = None


    def start(self):
        if self.thread and self.thread.is_alive():
            server_state.running = True
            log_bridge.log.emit(f"Server initialized in: {server_cfg["protocol"]}//:{server_cfg["host"]}:{server_cfg["port"]}")
            return

        log_bridge.log.emit(f"Server initialized in: {server_cfg["protocol"]}//:{server_cfg["host"]}:{server_cfg["port"]}")

        init_db(self.cfg)
        server_state.running = True

        self.thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )

        self.thread.start()


    def _run_server(self):

        serve(
            app,
            host=server_cfg["host"],
            port=server_cfg["port"],
            threads=server_cfg["threads"],
            connection_limit=server_cfg["connection_limit"],  # max connections concurrent
            backlog=server_cfg["backlog"],  # socket queue
            channel_timeout=server_cfg["channel_timeout"],  # kills hanging customers
            cleanup_interval=server_cfg["cleanup_interval"]  # kills dead connections
        )


    def stop(self):

        log_bridge.log.emit(f"Server stopped")
        server_state.running = False


    def restart(self):

        log_bridge.log.emit(f"Server restart")

        server_state.running = False
        server_state.running = True
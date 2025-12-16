import json
import subprocess
import os
import sys
import psutil
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from threading import Thread


PID_FILE = "pulseconnector.pid"


with open("config.json") as f:
    cfg = json.load(f)
    server_cfg = cfg["server"]


class ServerController(QObject):

    log = Signal(str)


    def __init__(self, script_path):
        super().__init__()
        self.script_path = Path(script_path)
        self.proc = None


    def start(self):

        try:
            port = server_cfg["port"]

            self.log.emit("Verifying and closing orphaned processes…")

            self.ensure_clean_state(port)

            self.proc = subprocess.Popen(
                [sys.executable, str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            Thread(target=self._read_logs, daemon=True).start()

            with open(PID_FILE, "w") as f:
                f.write(str(self.proc.pid))

            self.log.emit(f"Server initialized in PID: {self.proc.pid}")
            self.log.emit(f"Server initialized in: {server_cfg["protocol"]}//:{server_cfg["host"]}:{server_cfg["port"]}")
        except Exception as ex:
            self.log.emit(f"Error: {ex}")


    def stop(self):

        if os.path.exists(PID_FILE):

            pid = int(open(PID_FILE).read())
            psutil.Process(pid).terminate()
            os.remove(PID_FILE)
            self.log.emit(f"Server stopped in PID: {self.proc.pid}")


    def restart(self):

        self.log.emit(f"Server restart")
        self.stop()
        self.start()


    def ensure_clean_state(self, port):

        pid = self.find_server_pid_by_port(port)

        if pid:
            self.log.emit(f"Orphaned server detected (PID {pid}), cleaning...")

            p = psutil.Process(pid)
            p.terminate()

            try:
                p.wait(timeout=3)
            except psutil.TimeoutExpired:
                p.kill()


    def find_server_pid_by_port(self, port):

        for c in psutil.net_connections(kind="inet"):
            if c.laddr and c.laddr.port == port and c.status == psutil.CONN_LISTEN:
                return c.pid
        return None


    def _read_logs(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                if data.get("type") == "request":
                    msg = f"[{data['method']}] {data['path']}"
                    self.log.emit(msg)

            except json.JSONDecodeError:
                # Logs normales de waitress / prints
                self.log.emit(line)
import os
import sys
import threading
import time
from pathlib import Path

from sshtunnel import SSHTunnelForwarder

'''
class TunnelManager:
    def __init__(self, cfg):
        self.cfg = cfg
        self.tunnel = None
        self._thread = None
        self.running = False

    def start(self):
        if not self.cfg["ssh"]["enabled"]:
            return None
        if self.running:
            return self.tunnel
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        # espera corto para que arranque
        time.sleep(1)
        return self.tunnel

    def _run(self):
        cfg = self.cfg
        while True:
            try:
                self.tunnel = SSHTunnelForwarder(
                    (cfg["ssh"]["vps_host"], 22),
                    ssh_username=cfg["ssh"]["vps_user"],
                    ssh_password=cfg["ssh"].get("vps_pass"),
                    remote_bind_address=('127.0.0.1', cfg["ssh"]["remote_db_port"]),
                    local_bind_address=('127.0.0.1', cfg["ssh"]["local_bind_port"])
                )
                self.tunnel.start()
                self.running = True
                print("Túnel abierto. local port:", self.tunnel.local_bind_port)
                # bloqueo hasta que se caiga
                while self.tunnel.is_active:
                    time.sleep(1)
            except Exception as e:
                print("Tunnel error:", e)
                time.sleep(3)
            finally:
                try:
                    if self.tunnel:
                        self.tunnel.stop()
                except:
                    pass
                self.running = False

    def stop(self):
        try:
            if self.tunnel:
                self.tunnel.stop()
        except:
            pass
        self.running = False
'''

def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent

BASE_PATH = get_base_path()
CONFIG_PATH = BASE_PATH / "config.json"
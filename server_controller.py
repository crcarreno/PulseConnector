
import subprocess
import os
from pathlib import Path
import psutil

PID_FILE = "pulseconnector.pid"

class ServerController:

    def __init__(self, script_path):
        self.script_path = Path(script_path)
        self.proc = None


    def start(self):

        try:

            self.ensure_clean_state()

            self.proc = subprocess.Popen(
                ["python", str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            with open(PID_FILE, "w") as f:
                f.write(str(self.proc.pid))

            print("Init server...")
        except Exception as ex:
            print(ex)


    def stop(self):

        if os.path.exists(PID_FILE):

            pid = int(open(PID_FILE).read())
            psutil.Process(pid).terminate()
            os.remove(PID_FILE)
            print("Stop server...")


    def restart(self):

        print("Restart server...")
        self.stop()
        self.start()


    def ensure_clean_state(self):

        pid = self.find_server_pid_by_port(5000)

        if pid:
            print(f"Orphaned server detected (PID {pid}), cleaning...")
            p = psutil.Process(pid)
            p.terminate()

            try:
                p.wait(timeout=3)
            except psutil.TimeoutExpired:
                p.kill()

            print("Orphaned server delete")


    def find_server_pid_by_port(self, port):

        for c in psutil.net_connections(kind="inet"):
            if c.laddr and c.laddr.port == port and c.status == psutil.CONN_LISTEN:
                return c.pid
        return None

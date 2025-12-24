import ssl
import requests

from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import json
from utils import CONFIG_PATH


with open(CONFIG_PATH) as f:
    cfg = json.load(f)
    server_cfg = cfg["server"]
    secure_cfg = cfg["security"]

class ReverseProxyHandler(BaseHTTPRequestHandler):

    def _proxy(self):

        url = f"http://{server_cfg["internal_host"]}:{server_cfg["internal_port"]}{self.path}"

        headers = {k: v for k, v in self.headers.items()}
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        resp = requests.request(
            method=self.command,
            url=url,
            headers=headers,
            data=body,
            stream=True
        )

        self.send_response(resp.status_code)
        for k, v in resp.headers.items():
            if k.lower() != "transfer-encoding":
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(resp.content)

    def do_GET(self): self._proxy()
    def do_POST(self): self._proxy()
    def do_PUT(self): self._proxy()
    def do_DELETE(self): self._proxy()
    def do_PATCH(self): self._proxy()


def start_https_proxy(server_cfg):

    httpd = HTTPServer(
        (server_cfg["public_host"], server_cfg["public_port"]),
        ReverseProxyHandler
    )

    httpd.internal_host = server_cfg["internal_host"]
    httpd.internal_port = server_cfg["internal_port"]

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile=secure_cfg["cert"],
        keyfile=secure_cfg["key"]
    )

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()

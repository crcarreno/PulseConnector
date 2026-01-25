import ssl
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from utils.utils import CONFIG_PATH
from analytics.logger import setup_logger

log = setup_logger()

with open(CONFIG_PATH) as f:
    cfg = json.load(f)
    server_cfg = cfg["server"]
    secure_cfg = cfg["security"]


class ReverseProxyHandler(BaseHTTPRequestHandler):

    def _proxy(self):
        try:
            target_url = (
                f"http://{server_cfg['internal_host']}:"
                f"{server_cfg['internal_port']}{self.path}"
            )

            headers = {
                k: v
                for k, v in self.headers.items()
                if k.lower() not in (
                    "host",
                    "content-length",
                    "connection",
                )
            }

            body = self.rfile.read(
                int(self.headers.get("Content-Length", 0))
            )

            resp = requests.request(
                method=self.command,
                url=target_url,
                headers=headers,
                data=body,
                stream=True,
                timeout=30,
            )

            self.send_response(resp.status_code)

            for k, v in resp.headers.items():
                if k.lower() not in ("transfer-encoding", "content-length"):
                    self.send_header(k, v)

            # CORS para respuestas reales
            self.send_header(
                "Access-Control-Allow-Origin",
                "http://localhost:3000"
            )
            self.send_header(
                "Access-Control-Allow-Credentials",
                "true"
            )

            self.end_headers()
            self.wfile.write(resp.content)

        except Exception as e:
            log.exception("Proxy error")
            self.send_response(502)
            self.end_headers()

    def do_GET(self): self._proxy()
    def do_POST(self): self._proxy()
    def do_PUT(self): self._proxy()
    def do_DELETE(self): self._proxy()
    def do_PATCH(self): self._proxy()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header(
            "Access-Control-Allow-Origin",
            "http://localhost:3000"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization"
        )
        self.send_header(
            "Access-Control-Allow-Credentials",
            "true"
        )
        self.end_headers()


def start_https_proxy():
    try:
        httpd = HTTPServer(
            (server_cfg["public_host"], server_cfg["public_port"]),
            ReverseProxyHandler
        )

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            certfile=secure_cfg["cert"],
            keyfile=secure_cfg["key"]
        )

        httpd.socket = context.wrap_socket(
            httpd.socket,
            server_side=True
        )

        log.info(
            f"HTTPS proxy listening on "
            f"https://{server_cfg['public_host']}:"
            f"{server_cfg['public_port']}"
        )

        httpd.serve_forever()

    except Exception:
        log.exception("Failed to start HTTPS proxy")

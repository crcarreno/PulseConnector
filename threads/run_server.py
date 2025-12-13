import json

from waitress import serve
from web_route import create_app


with open("config.json") as f:
    cfg = json.load(f)
    server_cfg = cfg["server"]


app = create_app(cfg)

serve(
    app,
    host=server_cfg["host"],
    port=server_cfg["port"],
    threads=server_cfg["threads"],
    connection_limit=server_cfg["connection_limit"], # max connections concurrent
    backlog=server_cfg["backlog"], # socket queue
    channel_timeout=server_cfg["channel_timeout"], # kills hanging customers
    cleanup_interval=server_cfg["cleanup_interval"] # kills dead connections
)
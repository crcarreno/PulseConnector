import json
import os
import sys
from pathlib import Path
from utils import CONFIG_PATH
from certs.admin_certs import generate_ca, generate_server_cert, save_pem
from analytics.logger import setup_logger

log = setup_logger()


NAME_APP = "PulseConnector"

def install_certs(cfg):

    try:
        sec = cfg["security"]

        if sys.platform.startswith("win"):

            appdata = os.getenv("APPDATA")

            if not appdata:
                raise RuntimeError("No se pudo obtener APPDATA")

            path = Path(appdata) / NAME_APP / "certs"
            sec["cert"] = str(path / "cert.pem")
            sec["key"] = str(path / "key.pem")
            create_cert_dir(path)
            create_certs(path)
            save_config(cfg)
            log.info("Certs generated successfully")

            return 1


        elif sys.platform.startswith("linux"):

            path = Path.home() / ".config" / NAME_APP / "certs"
            sec["cert"] = str(path / "cert.pem")
            sec["key"] = str(path / "key.pem")
            create_cert_dir(path)
            create_certs(path)
            save_config(cfg)
            log.info("Certs generated successfully")

            return 1

    except Exception as e:
        log.error("Error: {}".format(e))
        raise e


def create_certs(path):

    try:
        if not (path / "cert.pem").exists():
            ca_key, ca_cert = generate_ca()
            server_key, server_cert = generate_server_cert(
                ca_key, ca_cert, hostname="localhost"
            )

            save_pem(path, server_key, server_cert)

    except Exception as e:
        log.error("Error: {}".format(e))
        raise e

def create_cert_dir(path):
    path.mkdir(parents=True, exist_ok=True)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)
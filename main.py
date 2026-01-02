# main.py
import json

from gui_main import run_gui
from install import install_certs
from utils import CONFIG_PATH
from analytics.analytics import Analytics
from analytics.logger import setup_logger

log = setup_logger()

if __name__ == "__main__":

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    try:

        analytics = Analytics()
        analytics.capture("app_start")

        analytics.send_daily_usage()

        install = install_certs(cfg)

        if install:
            log.info("Starting app")
            run_gui(cfg, analytics)
        else:
            log.error("Error installing certs")
            print("Error installing certs")

    except Exception as e:
        log.error("Error: {}".format(e))
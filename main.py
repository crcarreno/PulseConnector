# main.py
import json

from analytics import Analytics
from gui_main import run_gui
from install import install_certs
from utils import CONFIG_PATH

if __name__ == "__main__":

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    analytics = Analytics()
    analytics.capture("app_start")

    install = install_certs(cfg)

    if install:
        run_gui(cfg, analytics)
    else:
        print("Error installing certs")
# main.py
import json

from gui_main import run_gui
from install import install_certs
from utils import CONFIG_PATH

if __name__ == "__main__":

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    install = install_certs(cfg)

    if install:
        run_gui(cfg)
    else:
        print("Error installing certs")
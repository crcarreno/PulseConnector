# main.py
import json

from gui_main import run_gui
from utils import resource_path

if __name__ == "__main__":

    with open(resource_path("config.json")) as f:
        cfg = json.load(f)
    run_gui(cfg)

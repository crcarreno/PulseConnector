# main.py
import json
from gui_main import run_gui

if __name__ == "__main__":
    with open("config.json") as f:
        cfg = json.load(f)
    run_gui(cfg)

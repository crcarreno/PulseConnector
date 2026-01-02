import json
import os
import sys
from pathlib import Path
from datetime import date

APP_NAME = "PulseConnector"
USAGE_FILE = "usage.json"


def _today():
    return date.today().isoformat()


def _get_base_path():
    if sys.platform.startswith("win"):
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise RuntimeError("No se pudo obtener APPDATA")
        base = Path(appdata) / APP_NAME
    else:
        base = Path.home() / ".config" / APP_NAME

    base.mkdir(parents=True, exist_ok=True)
    return base


def _get_usage_path():
    return _get_base_path() / USAGE_FILE


def load_state():
    path = _get_usage_path()

    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}

    return {}


def save_state(state):
    path = _get_usage_path()
    path.write_text(json.dumps(state, indent=2))


def increment_request(kind="light", success=True):
    state = load_state()
    today = _today()

    day = state.setdefault(today, {
        "total": 0,
        "success": 0,
        "failed": 0,
        "light": 0,
        "heavy": 0,
        "sent": False
    })

    day["total"] += 1
    day["success" if success else "failed"] += 1
    day[kind] += 1

    save_state(state)

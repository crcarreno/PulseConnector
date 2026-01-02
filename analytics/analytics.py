import os
import sys
import uuid
import threading
import requests
import locale
import platform
import json
from pathlib import Path
from datetime import datetime
from datetime import date
from version import __version__


POSTHOG_API_KEY = "phc_lXEwU1I1SmWnyKbsZDoEDXUQXimcDRj4jViNMM6knPo"
POSTHOG_HOST = "https://app.posthog.com"
POSTHOG_ENDPOINT = f"{POSTHOG_HOST}/capture/"

APP_NAME = "PulseConnector"
APP_VERSION = __version__
USAGE_FILE = "usage.json"
STATE_FILE = "state.json"
TIMEOUT = 3


class Analytics:

    def __init__(self):
        self.uid = self._load_or_create_uid()


    def _get_base_path(self):
        if sys.platform.startswith("win"):
            appdata = os.getenv("APPDATA")
            if not appdata:
                raise RuntimeError("No se pudo obtener APPDATA")
            base = Path(appdata) / APP_NAME
        else:
            base = Path.home() / ".config" / APP_NAME

        base.mkdir(parents=True, exist_ok=True)
        return base


    def _get_state_path(self):
        return self._get_base_path() / STATE_FILE


    def _load_or_create_uid(self):
        path = self._get_state_path()

        if path.exists():
            try:
                return path.read_text().strip()
            except Exception:
                pass

        uid = str(uuid.uuid4())
        path.write_text(uid)
        return uid


    def _common_props(self):

        return {
            "app": APP_NAME,
            "version": APP_VERSION,
            "os": platform.system().lower(),
            "os_version": platform.version()
        }


    def capture_error(self, exc, component=None, severity="error", extra=None):
        properties = {
            **self._common_props(),
            "severity": severity,
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
            "component": component or "unknown"
        }

        if extra:
            properties.update(extra)

        payload = {
            "api_key": POSTHOG_API_KEY,
            "event": "error_occurred",
            "distinct_id": self.uid,
            "timestamp": datetime.utcnow().isoformat(),
            "properties": properties
        }

        threading.Thread(
            target=self._send,
            args=(payload,),
            daemon=True
        ).start()


    def capture(self, event_name, props=None):
        properties = self._common_props()

        if event_name == "app_start":
            properties.update({
                "app_mode": "gui",
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
                "locale": locale.getdefaultlocale()[0]
            })

        if props:
            properties.update(props)

        payload = {
            "api_key": POSTHOG_API_KEY,
            "event": event_name,
            "distinct_id": self.uid,
            "timestamp": datetime.utcnow().isoformat(),
            "properties": properties
        }

        threading.Thread(
            target=self._send,
            args=(payload,),
            daemon=True
        ).start()


    def _send(self, payload):
        try:
            requests.post(
                POSTHOG_ENDPOINT,
                json=payload,
                timeout=TIMEOUT
            )
        except Exception:
            pass


    def send_daily_usage(self):

        path = self._get_base_path() / USAGE_FILE
        if not path.exists():
            return

        try:
            state = json.loads(path.read_text())
        except Exception:
            return

        today = date.today().isoformat()
        changed = False

        for day, data in state.items():
            if day == today or data.get("sent"):
                continue

            payload = {
                "api_key": POSTHOG_API_KEY,
                "event": "daily_usage_summary",
                "distinct_id": self.uid,
                "timestamp": datetime.utcnow().isoformat(),
                "properties": {
                    **self._common_props(),
                    "date": day,
                    "requests_total": data["total"],
                    "requests_success": data["success"],
                    "requests_failed": data["failed"],
                    "requests_light": data["light"],
                    "requests_heavy": data["heavy"]
                }
            }

            self._send(payload)
            data["sent"] = True
            changed = True

        if changed:
            path.write_text(json.dumps(state, indent=2))



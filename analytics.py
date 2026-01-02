import uuid
import threading
from pathlib import Path
from datetime import datetime
import requests
import locale
import platform


POSTHOG_API_KEY = "phc_lXEwU1I1SmWnyKbsZDoEDXUQXimcDRj4jViNMM6knPo"
POSTHOG_HOST = "https://app.posthog.com"
POSTHOG_ENDPOINT = f"{POSTHOG_HOST}/capture/"

APP_NAME = "PulseConnector"
APP_VERSION = "1.2.0"

STATE_PATH = Path.home() / ".pulseconnector_state.json"
TIMEOUT = 3


class Analytics:
    def __init__(self):
        self.uid = self._load_or_create_uid()

    def _load_or_create_uid(self):
        if STATE_PATH.exists():
            try:
                return STATE_PATH.read_text().strip()
            except Exception:
                pass

        uid = str(uuid.uuid4())
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(uid)
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
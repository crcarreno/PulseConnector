from PySide6.QtCore import QObject, Signal

class LogBridge(QObject):
    log = Signal(str)

log_bridge = LogBridge()

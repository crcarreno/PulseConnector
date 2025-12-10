import json, requests
from collections import deque

from PySide6.QtGui import QAction, QIcon, Qt
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel, QFileDialog, \
    QComboBox, QApplication, QDialog, QMenuBar, QMessageBox, QHBoxLayout
from PySide6.QtCore import QThread, Signal, QObject

from gui_jsonConfig import JsonEditor, WindowConfig
from server import run_server
from utils import TunnelManager
import threading


class ServerThread(QThread):

    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self._stopped = False

    def run(self):
        run_server(self.cfg)  # blocking call; Flask internal server runs


class LogBridge(QObject):
    log = Signal(str)

class MainWindow(QWidget):

    def __init__(self, cfg):
        super().__init__()

        self.log_bridge = LogBridge()
        self.log_bridge.log.connect(self.append)

        self.log_buffer = deque(maxlen=5000)

        self.setWindowTitle("PulseConnector (server)")
        self.cfg = cfg

        # ===== Tamaño fijo =====
        self.setFixedSize(600, 450)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        self.setLayout(self.layout)

        # ===== Menú =====
        menubar = QMenuBar(self)
        self.layout.addWidget(menubar)

        menu_options = menubar.addMenu("Options")

        accion_settings = QAction("Settings", self)
        menu_options.addAction(accion_settings)
        accion_settings.triggered.connect(self._open_dialog_settings)

        accion_exit = QAction("Exit", self)
        menu_options.addAction(accion_exit)

        # ===== Título =====
        title = QLabel("Active / deactive server")
        title.setAlignment(Qt.AlignHCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 4px;")
        self.layout.addWidget(title)

        # ===== Botones Start/Stop =====
        btn_row = QHBoxLayout()

        self.btn_start = QPushButton(" Start")
        self.btn_start.setIcon(QIcon.fromTheme("media-playback-start"))
        self.btn_start.setFixedWidth(120)

        self.btn_stop = QPushButton(" Stop")
        self.btn_stop.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.btn_stop.setFixedWidth(120)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addStretch()

        self.layout.addLayout(btn_row)

        # ===== Selección de Base de Datos =====
        db_row = QHBoxLayout()

        self.db_label = QLabel("Select database:")
        self.db_label.setFixedWidth(120)

        self.db_combo = QComboBox()
        self.db_combo.setFixedWidth(160)

        self.db_sections = self._get_db_sections(cfg)

        dialect_list = [sec["dialect"] for sec in self.db_sections]

        self.db_combo.addItems(dialect_list)
        self._set_initial_selection()
        self.db_combo.currentTextChanged.connect(self._on_changed_dialect)

        db_row.addStretch()
        db_row.addWidget(self.db_label)
        db_row.addWidget(self.db_combo)
        db_row.addStretch()

        self.layout.addLayout(db_row)

        # ===== Terminal / Log =====
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.layout.addWidget(self.log)

        # Eventos
        self.server_thread = None
        self.tunnel = TunnelManager(self.cfg)
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)


    def _open_dialog_settings(self):

        if hasattr(self, "child") and self.child is not None:
            if self.child.isVisible():
                self.child.raise_()  # la trae adelante
                self.child.activateWindow()
                return

        with open("config.json", encoding="utf-8") as f:
            self.cfg = json.load(f)

        self.child = WindowConfig(self, self.cfg)
        self.child.show()


    def append(self, txt):
        self.log_buffer.append(txt)
        self.log.setPlainText("\n".join(self.log_buffer))
        self.log.verticalScrollBar().setValue(
            self.log.verticalScrollBar().maximum()  # auto-scroll al final
        )


    def start(self):
        try:
            #self.append("Init tunnel...")
            #self.tunnel.start()
            self.append("Init web server...")
            self.server_thread = threading.Thread(
                target=run_server,
                args=(self.cfg, self),
                daemon=True)
            self.server_thread.start()
            self.append("Server init in http://{host}:{port}".format(**self.cfg["server"]))
        except Exception as ex:
            self._get_error(self, ex)


    def stop(self):
        self.append("Stop tunnel and server...")
        self.tunnel.stop()
        # Producción usa waitress/gunicorn como servicio

        try:
            self.send_shutdown_request(self.cfg)
        except Exception:
            pass

        self.append("Done.")


    def edit_conf(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open config.json", "", "JSON files (*.json)")
        if fname:
            QMessageBox.information(self, "Info", f"Pulsaste abrir: {fname}\nEditar manualmente y reiniciar.")


    def _get_db_sections(self, cfg):
        sections = []
        for key, val in cfg.items():
            if key.startswith("db_") and isinstance(val, dict) and "dialect" in val:
                sections.append(val)
        return sections


    def _set_initial_selection(self):
        active = self.cfg.get("active_dialect")

        if active:
            idx = self.db_combo.findText(active)
            if idx >= 0:
                self.db_combo.setCurrentIndex(idx)
                return

        self.cfg["active_dialect"] = self.db_combo.currentText()


    def _on_changed_dialect(self, dialect):
        filename = "config.json"

        self.cfg["active_dialect"] = dialect

        with open(filename, "w") as f:
            json.dump(self.cfg, f, indent=4)


    def _get_section_by_dialect(self, dialect):
        for sec in self.db_sections:
            if sec["dialect"] == dialect:
                return sec
        return None

    def _get_error(self, error_text):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle("Error")
        box.setText(str(error_text))
        box.exec()

def run_gui(cfg):
    app = QApplication([])
    win = MainWindow(cfg)
    win.resize(600, 400)
    win.show()
    return app.exec_()

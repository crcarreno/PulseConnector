import json

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLabel, QFileDialog, \
    QComboBox, QApplication, QDialog, QMenuBar, QMessageBox
from PySide6.QtCore import QThread, Signal

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


class MainWindow(QWidget):

    def __init__(self, cfg):

        super().__init__()

        self.setWindowTitle("PulseConnect OData (Community)")

        self.layout = QVBoxLayout()

        self.cfg = cfg

        #-- Menú principal - --
        menubar = QMenuBar(self)

        self.layout.addWidget(menubar)

        # Crear menús
        menu_options = menubar.addMenu("Options")

        accion_settings = QAction("Settings", self)
        menu_options.addAction(accion_settings)

        accion_settings.triggered.connect(self._open_dialog_settings)

        accion_exit = QAction("Exit", self)
        menu_options.addAction(accion_exit)

        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")

        # --- Combo de dialectos ---
        self.db_label = QLabel("Tipo de Base de Datos:")
        self.db_combo = QComboBox()

        # Cargar dialectos desde el JSON
        self.db_sections = self._get_db_sections(cfg)
        dialect_list = [sec["dialect"] for sec in self.db_sections]

        self.db_combo.addItems(dialect_list)
        self._set_initial_selection()

        # Capturar cambios del usuario
        self.db_combo.currentTextChanged.connect(self.on_db_change)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.layout.addWidget(QLabel("Conector OData"))
        self.layout.addWidget(self.btn_start)
        self.layout.addWidget(self.btn_stop)
        self.layout.addWidget(self.db_combo)

        self.layout.addWidget(self.log)
        self.setLayout(self.layout)
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
        self.log.append(txt)

    def start(self):
        try:
            #self.append("Init tunnel...")
            #self.tunnel.start()
            self.append("Init web server...")
            self.server_thread = threading.Thread(target=run_server, args=(self.cfg,), daemon=True)
            self.server_thread.start()
            self.append("Server init in http://{host}:{port}".format(**self.cfg["server"]))
        except Exception as ex:
            self._get_error(self, ex)


    def stop(self):
        self.append("Stop tunnel and server...")
        self.tunnel.stop()
        # detener Flask dev server no es trivial; en producción usa waitress/gunicorn como servicio
        self.append("Done.")

    def edit_conf(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open config.json", "", "JSON files (*.json)")
        if fname:
            QMessageBox.information(self, "Info", f"Pulsaste abrir: {fname}\nEditar manualmente y reiniciar.")

    # -----------------------------
    # Encuentra secciones tipo db_xxx
    # -----------------------------
    def _get_db_sections(self, cfg):
        sections = []
        for key, val in cfg.items():
            if key.startswith("db_") and isinstance(val, dict) and "dialect" in val:
                sections.append(val)
        return sections

    # -----------------------------
    # Seleccionar automáticamente el dialecto activo
    # -----------------------------
    def _set_initial_selection(self):
        # Si ya existe un "active_dialect" almacenado
        active = self.cfg.get("active_dialect")
        if active:
            idx = self.db_combo.findText(active)
            if idx >= 0:
                self.db_combo.setCurrentIndex(idx)
                return

        # Si no hay activo, poner el primero
        self.cfg["active_dialect"] = self.db_combo.currentText()

    # -----------------------------
    # Cuando el usuario cambia la BD
    # -----------------------------
    def on_db_change(self, dialect):
        print(f"Dialecto seleccionado: {dialect}")
        self.cfg["active_dialect"] = dialect

        # Si quieres, puedes obtener la sección completa:
        selected_cfg = self._get_section_by_dialect(dialect)
        print("Config de la DB seleccionada:", selected_cfg)

    # -----------------------------
    # Busca sección por dialecto
    # -----------------------------
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

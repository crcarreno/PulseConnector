from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout
)


class JsonEditor(QWidget):
    def __init__(self, json_data: dict, parent=None):
        super().__init__(parent)
        self.json_data = json_data

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])

        self._populate_tree(self.json_data)

        # Expandir árbol automáticamente
        self.tree.expandAll()

        # Escuchar cambios en las celdas
        self.tree.itemChanged.connect(self._on_item_changed)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)

    # -----------------------------
    # POBLAR ÁRBOL
    # -----------------------------
    def _populate_tree(self, data, parent_item=None):
        for key, value in data.items():

            # Si es diccionario → nodo padre
            if isinstance(value, dict):
                item = QTreeWidgetItem([key, ""])
                item.setFlags(item.flags() | Qt.ItemIsEditable)

                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

                # Recursión
                self._populate_tree(value, item)

            else:
                # Nodo hoja → tiene key + value en una sola fila
                item = QTreeWidgetItem([key, str(value)])
                item.setFlags(item.flags() | Qt.ItemIsEditable)

                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

    # -----------------------------
    # RECONSTRUIR JSON DESDE EL ÁRBOL
    # -----------------------------
    def get_json(self):
        def read(item):
            key = item.text(0)
            child_count = item.childCount()

            # Nodo hoja con key/value
            if child_count == 0:
                return key, self._convert_value(item.text(1))

            # Nodo padre (dict)
            obj = {}
            for i in range(child_count):
                k, v = read(item.child(i))
                obj[k] = v
            return key, obj

        result = {}
        for i in range(self.tree.topLevelItemCount()):
            k, v = read(self.tree.topLevelItem(i))
            result[k] = v

        return result

    # -----------------------------
    # ACTUALIZAR JSON EN CUANTO SE MODIFICA UN NODO
    # -----------------------------
    def _on_item_changed(self, item, column):
        # Actualizamos el dict original
        self.json_data = self.get_json()

    # -----------------------------
    # CONVERTIR TIPOS
    # -----------------------------
    def _convert_value(self, v: str):
        v = v.strip()

        # Bool
        if v.lower() == "true": return True
        if v.lower() == "false": return False

        # Int
        try:
            return int(v)
        except:
            pass

        # Float
        try:
            return float(v)
        except:
            pass

        # String
        return v

from PySide6.QtGui import Qt
from PySide6.QtWidgets import (QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QDialog, QLabel, QPushButton)

class WindowConfig(QDialog):

    def __init__(self, parent, cfg):

        super().__init__(parent)

        self.setWindowTitle("Settings")

        self.editor = JsonEditor(cfg)

        layout = QVBoxLayout()

        btn = QPushButton("Close")
        btn.clicked.connect(self.close)

        layout.addWidget(self.editor)

        layout.addWidget(btn)

        self.setLayout(layout)
        self.resize(400, 600)


class JsonEditor(QWidget):

    FILENAME = "config.json"

    def __init__(self, json_data: dict, parent=None):

        super().__init__(parent)

        self.json_data = json_data

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])

        self._populate_tree(self.json_data)

        self.tree.expandAll()

        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)

        self.tree.itemChanged.connect(self._on_item_changed)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)


    def _save_to_file(self):
        import json
        with open(self.FILENAME, "w", encoding="utf-8") as f:
            json.dump(self.json_data, f, indent=4, ensure_ascii=False)


    def _populate_tree(self, data, parent_item=None):

        for key, value in data.items():

            if isinstance(value, dict):
                item = QTreeWidgetItem([key, ""])
                item.setFlags(item.flags() | Qt.ItemIsEditable)

                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)

                self._populate_tree(value, item)

            else:
                # Nodo hoja → tiene key + value en una sola fila
                item = QTreeWidgetItem([key, str(value)])
                item.setFlags(item.flags() | Qt.ItemIsEditable)

                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree.addTopLevelItem(item)


    def get_json(self):
        def read(item):
            key = item.text(0)
            child_count = item.childCount()

            if child_count == 0:
                return key, self._convert_value(item.text(1))

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


    def _on_item_changed(self, item, column):
        self.json_data = self.get_json()
        self._save_to_file()


    def _convert_value(self, v: str):
        v = v.strip()

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
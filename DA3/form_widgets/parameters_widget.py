from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QListWidget, QPushButton, QListWidgetItem,
                               QLabel, QApplication, QMainWindow, QTextEdit,
                               QWidget, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from typing import List, Optional, Tuple


class ParametersWidget(QWidget):
    """Виджет параметров с кнопкой запуска редактора"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button = QPushButton("Запустить редактор")
        button.clicked.connect(self.launch_editor)
        layout.addWidget(button)
        self.setStyleSheet("background-color: #fff0e6;")

    def launch_editor(self):
        QMessageBox.information(self, "Редактор", "Редактор запущен")
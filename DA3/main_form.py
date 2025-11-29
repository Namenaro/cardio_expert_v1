from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QListWidget, QPushButton, QListWidgetItem,
                               QLabel, QApplication, QMainWindow, QTextEdit)
from PySide6.QtCore import Qt
from typing import List, Optional, Tuple




class MainForm(QMainWindow):
    """Главная форма приложения"""

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Главная форма приложения")
        self.resize(600, 400)


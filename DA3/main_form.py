from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QListWidget, QPushButton, QListWidgetItem,
                               QLabel, QApplication, QMainWindow, QTextEdit)
from PySide6.QtCore import Qt
from typing import List, Optional, Tuple




class MainForm(QMainWindow):
    """Главная форма приложения"""

    def __init__(self, selected_form_id: Optional[int] = None, create_new: bool = False):
        super().__init__()
        self.selected_form_id = selected_form_id
        self.create_new = create_new
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Главная форма приложения")
        self.resize(600, 400)

        central_widget = QTextEdit()
        self.setCentralWidget(central_widget)

        if self.create_new:
            central_widget.setText("Режим создания новой формы")
        elif self.selected_form_id:
            central_widget.setText(f"Работа с формой ID: {self.selected_form_id}")
        else:
            central_widget.setText("Главная форма приложения")
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt


class PCsWidget(QWidget):


    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button = QPushButton("Запустить редактор")
        button.clicked.connect(self.launch_editor)
        layout.addWidget(button)
        self.setStyleSheet("background-color: #ffe6e6;")

    def launch_editor(self):
        QMessageBox.information(self, "Редактор", "Редактор запущен")
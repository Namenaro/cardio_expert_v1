# DA3/simulation_app/simulation_widgets/empty_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class EmptyWidget(QWidget):
    """Пустой виджет для правой панели"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.info_label = None
        self.error_label = None
        self.layout = None
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.info_label = QLabel("Правая панель\n(ничего не выбрано)")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                font-style: italic;
            }
        """)
        self.layout.addWidget(self.info_label)

    def set_error_message(self, message: str):
        """Показывает сообщение об ошибке"""
        self._clear_layout()

        self.error_label = QLabel(f"Ошибка:\n{message}")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                font-size: 12px;
                font-weight: bold;
                background-color: #ffebee;
                padding: 10px;
                border: 1px solid #f44336;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.error_label)

    def clear_error(self):
        """Очищает сообщение об ошибке и показывает стандартный текст"""
        self._clear_layout()
        self.layout.addWidget(self.info_label)

    def cleanup(self):
        """Очищает ресурсы"""
        self._clear_layout()
        self.info_label = None
        self.error_label = None

    def _clear_layout(self):
        """Очищает layout от всех виджетов"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
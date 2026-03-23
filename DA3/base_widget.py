from PySide6.QtWidgets import QWidget
from utils.style_loader import get_style_loader


class BaseWidget(QWidget):
    """Базовый класс для всех виджетов с поддержкой стилей"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.style_loader = get_style_loader()

    def apply_styles(self, *style_files: str) -> None:
        """Применить стили к виджету"""
        self.style_loader.apply_style(self, *style_files)

    def reload_styles(self) -> None:
        """Перезагрузить стили (для динамической смены тем)"""
        # Переопределить в наследниках
        pass

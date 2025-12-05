from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from CORE.db_dataclasses import BaseClass


class ClassesListWidget(QWidget):
    """Виджет для отображения и выбора классов"""
    class_selected = Signal(BaseClass)

    def __init__(self, full_classes: List[BaseClass], parent=None):
        super().__init__(parent)
        self._classes = full_classes  # Гарантированно полные
        self._selected_class = None
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса виджета"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        self._populate_list()

    def _populate_list(self):
        """Заполнение списка классами"""
        self.list_widget.clear()
        for class_ref in self._classes:
            item = QListWidgetItem(f"ID: {class_ref.id} | {class_ref.name}")
            item.setData(Qt.ItemDataRole.UserRole, class_ref)
            self.list_widget.addItem(item)

    def _on_item_clicked(self, item):
        """Обработчик клика по элементу списка"""
        if class_ref := item.data(Qt.ItemDataRole.UserRole):
            self._selected_class = class_ref
            self.class_selected.emit(class_ref)

    def get_selected_class(self) -> BaseClass:
        """Получить выбранный класс"""
        return self._selected_class

    def set_selected_class(self, class_ref: BaseClass):
        """Установить выбранный класс"""
        self._selected_class = class_ref
        if class_ref is None:
            self.list_widget.clearSelection()
            return

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item_class := item.data(Qt.ItemDataRole.UserRole):
                if item_class.id == class_ref.id:
                    self.list_widget.setCurrentItem(item)
                    break
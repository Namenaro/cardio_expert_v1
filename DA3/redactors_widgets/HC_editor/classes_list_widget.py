from typing import Optional, List
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QFormLayout, QGroupBox, QComboBox, QWidget, QMessageBox, QVBoxLayout, QListWidget,
    QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from CORE.db_dataclasses import BasePazzle, Form, BaseClass
from DA3 import app_signals
from DA3.redactors_widgets import BaseEditor

class ClassesListWidget(QWidget):
    """Виджет для отображения и выбора классов"""

    # Сигнал выбора класса
    class_selected = Signal(BaseClass)

    def __init__(self, classes: Optional[List[BaseClass]] = None, parent=None):
        super().__init__(parent)
        self._classes = classes or []
        self._selected_class: Optional[BaseClass] = None

        self.setup_ui()
        self.populate_list()

    def setup_ui(self):
        """Настройка интерфейса виджета"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Список классов
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)




    def populate_list(self, classes: Optional[List[BaseClass]] = None):
        """Заполнение списка классами"""
        if classes is not None:
            self._classes = classes

        self.list_widget.clear()
        self._selected_class = None


        for class_ref in self._classes:
            if hasattr(class_ref, 'id') and class_ref.id is not None:
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, class_ref)

                # Формируем текст для отображения
                display_text = f"ID: {class_ref.id}"

                if hasattr(class_ref, 'name') and class_ref.name:
                    display_text += f" | Имя: {class_ref.name}"

                if hasattr(class_ref, 'type') and class_ref.type:
                    display_text += f" | Тип: {class_ref.type}"

                if hasattr(class_ref, 'comment') and class_ref.comment:
                    # Обрезаем длинный комментарий
                    comment = class_ref.comment
                    if len(comment) > 50:
                        comment = comment[:47] + "..."
                    display_text += f"\nКомментарий: {comment}"

                item.setText(display_text)
                self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        """Обработчик клика по элементу списка"""
        class_ref = item.data(Qt.ItemDataRole.UserRole)
        if class_ref:
            self._selected_class = class_ref

            # Испускаем сигнал
            self.class_selected.emit(class_ref)

    def get_selected_class(self) -> Optional[BaseClass]:
        """Получить выбранный класс"""
        return self._selected_class

    def set_selected_class(self, class_ref: Optional[BaseClass]):
        """Установить выбранный класс"""
        if class_ref is None:
            self.list_widget.clearSelection()
            self._selected_class = None
            return

        self._selected_class = class_ref

        # Ищем и выбираем элемент в списке
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_class = item.data(Qt.ItemDataRole.UserRole)
            if item_class and hasattr(item_class, 'id') and item_class.id == class_ref.id:
                self.list_widget.setCurrentItem(item)
                break

    def clear_selection(self):
        """Очистить выбор"""
        self.list_widget.clearSelection()
        self._selected_class = None


    def get_classes(self) -> List[BaseClass]:
        """Получить список классов"""
        return self._classes.copy()
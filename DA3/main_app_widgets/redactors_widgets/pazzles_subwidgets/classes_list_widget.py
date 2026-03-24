from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from CORE.db_dataclasses import BaseClass


class ClassListItemWidget(QWidget):
    def __init__(self, class_ref, parent=None):
        super().__init__(parent)
        self.class_ref = class_ref

        # Основной горизонтальный макет
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(8)

        # Label для ID
        self.id_label = QLabel(f"ID: {class_ref.id}")
        self.id_label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.id_label)

        # Label для названия (жирный шрифт)
        self.name_label = QLabel(class_ref.name)
        font = self.name_label.font()
        font.setBold(True)
        self.name_label.setFont(font)
        self.name_label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.name_label)

        # Label для комментария (меньший размер шрифта)
        self.comment_label = QLabel(class_ref.comment)
        font = self.comment_label.font()
        font.setPointSize(font.pointSize() - 1)  # на 1 пункт меньше
        self.comment_label.setFont(font)
        self.comment_label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self.comment_label)

        # Растягиваем последний элемент (комментарий), чтобы заполнить пространство
        layout.addStretch()

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
        """Заполнение списка классами с кастомными виджетами"""
        self.list_widget.clear()

        for class_ref in self._classes:
            # Создаём элемент списка
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, class_ref)

            # Создаём виджет для элемента
            widget = ClassListItemWidget(class_ref, self.list_widget)
            item.setSizeHint(widget.sizeHint())  # чтобы список корректно учитывал размер

            # Добавляем элемент и привязываем виджет
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def _on_item_clicked(self, item):
        """Обработчик клика по элементу списка"""
        # Получаем данные из QListWidgetItem, а не из виджета
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
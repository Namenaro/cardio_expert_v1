from typing import Optional, List
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QFormLayout, QGroupBox, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QWidget, QHeaderView, QHBoxLayout
)
from PySide6.QtCore import Qt
from CORE.db_dataclasses import ClassArgument, ObjectArgumentValue



class ArgumentsTableWidget(QWidget):
    """Виджет для отображения и редактирования аргументов конструктора класса"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._arguments: List[ClassArgument] = []
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса виджета"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        self.title_label = QLabel("Аргументы конструктора класса:")
        self.title_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(self.title_label)

        # Таблица
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Имя", "Тип", "Комментарий", "Значение"])

        # Настройка внешнего вида таблицы
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Имя
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Тип
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Комментарий
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Значение

        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setMinimumHeight(200)

        layout.addWidget(self.table_widget)

    def load_arguments(self, arguments: List[ClassArgument]):
        """Загрузка списка аргументов в таблицу"""
        self._arguments = arguments
        self.table_widget.setRowCount(len(arguments))

        for row, arg in enumerate(arguments):
            # ID аргумента
            id_item = QTableWidgetItem(str(arg.id) if arg.id else "")
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 0, id_item)

            # Имя аргумента
            name_item = QTableWidgetItem(arg.name if arg.name else "")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 1, name_item)

            # Тип данных
            type_item = QTableWidgetItem(arg.data_type if arg.data_type else "")
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 2, type_item)

            # Комментарий
            comment_item = QTableWidgetItem(arg.comment if arg.comment else "")
            comment_item.setFlags(comment_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 3, comment_item)

            # Значение (редактируемое)
            value_item = QTableWidgetItem(arg.default_value if arg.default_value else "")
            value_item.setFlags(value_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 4, value_item)

        # Обновляем заголовок
        self.title_label.setText(f"Аргументы конструктора класса ({len(arguments)}):")

    def get_argument_values(self) -> List[ObjectArgumentValue]:
        """Получить значения аргументов из таблицы"""
        values = []
        for row, arg in enumerate(self._arguments):
            value_item = self.table_widget.item(row, 4)
            argument_value = value_item.text().strip() if value_item else ""

            # Создаем ObjectArgumentValue
            obj_arg_value = ObjectArgumentValue(
                id=None,
                object_id=None,
                argument_id=arg.id,
                argument_value=argument_value
            )
            values.append(obj_arg_value)

        return values

    def clear(self):
        """Очистить таблицу"""
        self._arguments = []
        self.table_widget.setRowCount(0)
        self.title_label.setText("Аргументы конструктора класса:")

    def has_data(self) -> bool:
        """Проверить, есть ли данные в таблице"""
        return len(self._arguments) > 0



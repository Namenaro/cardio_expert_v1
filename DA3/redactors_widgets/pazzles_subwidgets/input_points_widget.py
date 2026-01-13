from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QComboBox
)
from PySide6.QtCore import Qt, Signal
from CORE.db_dataclasses import *


class InputPointsWidget(QWidget):
    """Виджет для редактирования входных точек объекгта"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._input_points: List[ClassInputPoint] = []
        self._current_values: List[ObjectInputPointValue] =[]
        self.setup_ui()


    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        self.title_label = QLabel("Входные точки:")
        self.title_label.setStyleSheet("font-weight: bold; color: #ff0000;")
        layout.addWidget(self.title_label)

        # Таблица
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels([
            "Название точки класса КЛАССА",
            "Название точки ФОРМЫ",
            "Коммент"
        ])

        # Настройка внешнего вида таблицы
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Название точки ФОРМЫ
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Коммент

        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setMinimumHeight(150)

        layout.addWidget(self.table_widget)


    def load_input_points(self,
                          input_points: List[ClassInputPoint],
                          form_points: List[Point]):
        """
        Загрузка списка входных точек класса и точек формы

        Args:
            input_points: Список входных points класса
            form_points: Список points формы
        """
        self._input_points = input_points
        self.table_widget.setRowCount(len(input_points))

        for row, input_point in enumerate(input_points):
            # Название точки класса (нередактируемое)
            name_item = QTableWidgetItem(input_point.name if input_point.name else "")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 0, name_item)

            # Название точки формы (выпадающий список)
            combo_widget = QComboBox()
            combo_widget.addItem("", None)  # Пустой вариант
            for point in form_points:
                display_text = f"{point.name} (ID: {point.id})"
                combo_widget.addItem(display_text, point.id)

            # Устанавливаем текущую выбранную точку, если есть
            current_value = self._get_current_point_value(input_point.id)
            if current_value and current_value.point_id:
                self._select_combo_item(combo_widget, current_value.point_id)
                combo_widget.setStyleSheet("")  # Сбрасываем стиль если выбрано
            else:
                combo_widget.setStyleSheet("background-color: #ffcccc;")  # Красный если не выбрано

            combo_widget.currentIndexChanged.connect(self._on_point_selected)


            self.table_widget.setCellWidget(row, 1, combo_widget)



    def _get_current_point_value(self, input_point_id: int) -> Optional[ObjectInputPointValue]:
        """Получить текущее значение точки"""
        for value in self._current_values:
            if value.input_point_id == input_point_id:
                return value
        return None

    def _select_combo_item(self, combo_box: QComboBox, point_id: int):
        """Выбрать элемент в комбобоксе по ID точки"""
        for i in range(combo_box.count()):
            if combo_box.itemData(i) == point_id:
                combo_box.setCurrentIndex(i)
                break


    def _on_point_selected(self, index: int):
        """Обработчик выбора точки формы"""
        combo_box = self.sender()
        if not isinstance(combo_box, QComboBox):
            return
        point_id = combo_box.currentData()
        row = self.table_widget.indexAt(combo_box.pos()).row()

        # Подсветка ячейки в зависимости от выбора
        if point_id is None:
            combo_box.setStyleSheet("background-color: #ffcccc;")  # Красный для незаполненного
        else:
            combo_box.setStyleSheet("")  # Сбрасываем стиль

        if row < len(self._input_points):
            input_point = self._input_points[row]

            # Обновляем или создаем значение
            value = self._get_current_point_value(input_point.id)
            if not value:
                value = ObjectInputPointValue(
                    id=None,
                    object_id=None,
                    input_point_id=input_point.id,
                    point_id=point_id
                )
                self._current_values.append(value)
            else:
                value.point_id = point_id

    def get_input_point_values(self) -> List[ObjectInputPointValue]:
        """Получить значения входных параметров"""
        return self._current_values.copy()

    def load_current_values(self, values: List[ObjectInputPointValue]):
        """Загрузить текущие значения из объекта"""
        self._current_values = values.copy()

        # Обновляем подсветку в таблице если она уже загружена
        if self._input_points:
            for row in range(self.table_widget.rowCount()):
                combo_widget = self.table_widget.cellWidget(row, 1)
                if combo_widget:
                    if id_item := self.table_widget.item(row, 0):
                        point_name = id_item.text()
                        # Находим соответствующий input_point
                        input_point = next((p for p in self._input_points
                                            if p.name == point_name), None)
                        if input_point:
                            value = self._get_current_point_value(input_point.id)
                            if value and value.point_id:
                                self._select_combo_item(combo_widget, value.point_id)
                                combo_widget.setStyleSheet("")  # Сбрасываем стиль
                            else:
                                combo_widget.setStyleSheet("background-color: #ffcccc;")  # Красный


    def validate(self) -> bool:
        """
        Корректность заполнения данных пользователем

        Returns:
            True - корректо, False - некорректно
        """
        if not self._input_points:
            return True

        for input_point in self._input_points:
            if input_point.id is None:
                continue

            # Ищем значение для этой точки
            value = self._get_current_point_value(input_point.id)
            if not value or value.point_id is None:
                return False

        return True

    def get_validation_errors(self) -> str:
        """
        Получить ообщение с подробностями проблем валидации

        Returns:
            Сообщение с подробностями проблем валидации
        """
        errors = []

        for input_point in self._input_points:
            if input_point.id is None:
                continue

            value = self._get_current_point_value(input_point.id)
            if not value or value.point_id is None:
                point_name = input_point.name if input_point.name else f"ID:{input_point.id}"
                errors.append(point_name)

        params_list = "\n• " + "\n• ".join(errors)
        error_str = f"Для следующих входных точек класса необходимо выбрать точки формы:\n{params_list}"

        return error_str











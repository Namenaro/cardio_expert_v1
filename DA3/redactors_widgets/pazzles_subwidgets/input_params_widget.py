from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QComboBox
)
from PySide6.QtCore import Qt, Signal
from CORE.db_dataclasses import ClassInputParam, Parameter, ObjectInputParamValue


class InputParamsWidget(QWidget):
    """Виджет для редактирования входных параметров объекта"""


    def __init__(self, parent=None):
        super().__init__(parent)
        self._input_params: List[ClassInputParam] = []
        self._current_values: List[ObjectInputParamValue] = []
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса виджета"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        self.title_label = QLabel("Входные параметры:")
        self.title_label.setStyleSheet("font-weight: bold; color: #ff0000;")
        layout.addWidget(self.title_label)

        # Таблица
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels([
            "Название параметра КЛАССА",
            "Название параметра ФОРМЫ",
            "Тип данных",
            "Коммент"
        ])

        # Настройка внешнего вида таблицы
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Имя класса
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Параметр формы
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Тип данных
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Коммент

        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setMinimumHeight(150)

        layout.addWidget(self.table_widget)

    def load_input_params(self,
                          input_params: List[ClassInputParam],
                          form_parameters: List[Parameter]):
        """
        Загрузка списка входных параметров и параметров формы

        Args:
            input_params: Список входных параметров класса
            form_parameters: Список параметров формы
        """
        self._input_params = input_params
        self.table_widget.setRowCount(len(input_params))

        for row, input_param in enumerate(input_params):
            # Название параметра класса (нередактируемое)
            name_item = QTableWidgetItem(input_param.name if input_param.name else "")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 0, name_item)

            # Название параметра формы (выпадающий список)
            combo_widget = QComboBox()
            combo_widget.addItem("", None)  # Пустой вариант
            for param in form_parameters:
                display_text = f"{param.name} (ID: {param.id})"
                combo_widget.addItem(display_text, param.id)

            # Устанавливаем текущий выбранный параметр, если есть
            current_value = self._get_current_param_value(input_param.id)
            if current_value and current_value.parameter_id:
                self._select_combo_item(combo_widget, current_value.parameter_id)
                combo_widget.setStyleSheet("")  # Сбрасываем стиль если выбрано
            else:
                combo_widget.setStyleSheet("background-color: #ffcccc;")  # Красный если не выбрано

            combo_widget.currentIndexChanged.connect(self._on_param_selected)


            self.table_widget.setCellWidget(row, 1, combo_widget)

            # Тип данных (нередактируемое)
            type_item = QTableWidgetItem(input_param.data_type if input_param.data_type else "")
            type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 2, type_item)

            comment_item = QTableWidgetItem(input_param.comment if input_param.comment else "")
            comment_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row, 3, comment_item)



    def _get_current_param_value(self, input_param_id: int) -> Optional[ObjectInputParamValue]:
        """Получить текущее значение параметра"""
        for value in self._current_values:
            if value.input_param_id == input_param_id:
                return value
        return None

    def _select_combo_item(self, combo_box: QComboBox, parameter_id: int):
        """Выбрать элемент в комбобоксе по ID параметра"""
        for i in range(combo_box.count()):
            if combo_box.itemData(i) == parameter_id:
                combo_box.setCurrentIndex(i)
                break

    def _on_param_selected(self, index: int):
        """Обработчик выбора параметра формы"""
        combo_box = self.sender()
        if not isinstance(combo_box, QComboBox):
            return
        parameter_id = combo_box.currentData()
        row = self.table_widget.indexAt(combo_box.pos()).row()

        # Подсветка ячейки в зависимости от выбора
        if parameter_id is None:
            combo_box.setStyleSheet("background-color: #ffcccc;")  # Красный для незаполненного
        else:
            combo_box.setStyleSheet("")  # Сбрасываем стиль

        if row < len(self._input_params):
            input_param = self._input_params[row]

            # Обновляем или создаем значение
            value = self._get_current_param_value(input_param.id)
            if not value:
                value = ObjectInputParamValue(
                    id=None,
                    object_id=None,
                    input_param_id=input_param.id,
                    parameter_id=parameter_id
                )
                self._current_values.append(value)
            else:
                value.parameter_id = parameter_id


    def validate(self) -> bool:
        """
        Проверка, что для всех входных параметров выбраны параметры формы

        Returns:
            True - все параметры выбраны, False - есть незаполненные параметры
        """
        if not self._input_params:
            return True  # Нет параметров - нечего проверять

        # Проверяем каждый входной параметр
        for input_param in self._input_params:
            if input_param.id is None:
                continue

            # Ищем значение для этого параметра
            value = self._get_current_param_value(input_param.id)

            # Если значение не найдено или parameter_id не установлен
            if not value or value.parameter_id is None:
                return False

        return True

    def get_validation_errors(self) -> str:
        """
        Получить список незаполненных параметров

        Returns:
            Сообщение с подробностями проблем валидации
        """
        errors = []

        for input_param in self._input_params:
            if input_param.id is None:
                continue

            value = self._get_current_param_value(input_param.id)
            if not value or value.parameter_id is None:
                param_name = input_param.name if input_param.name else f"ID:{input_param.id}"
                errors.append(param_name)

        params_list = "\n• " + "\n• ".join(errors)
        error_str = f"Для следующих входных параметров класса необходимо выбрать параметры формы:\n{params_list}"

        return error_str

    def get_input_param_values(self) -> List[ObjectInputParamValue]:
        """Получить значения входных параметров"""
        return self._current_values.copy()

    def load_current_values(self, values: List[ObjectInputParamValue]):
        """Загрузить текущие значения из объекта"""
        self._current_values = values.copy()

        # Обновляем подсветку в таблице если она уже загружена
        if self._input_params:
            for row in range(self.table_widget.rowCount()):
                combo_widget = self.table_widget.cellWidget(row, 1)
                if combo_widget:
                    if id_item := self.table_widget.item(row, 0):
                        param_name = id_item.text()
                        # Находим соответствующий input_param
                        input_param = next((p for p in self._input_params
                                            if p.name == param_name), None)
                        if input_param:
                            value = self._get_current_param_value(input_param.id)
                            if value and value.parameter_id:
                                self._select_combo_item(combo_widget, value.parameter_id)
                                combo_widget.setStyleSheet("")  # Сбрасываем стиль
                            else:
                                combo_widget.setStyleSheet("background-color: #ffcccc;")  # Красный

    def clear(self):
        """Очистить виджет"""
        self._input_params = []
        self._current_values = []
        self.table_widget.setRowCount(0)



import logging
from typing import Optional, List, Any
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout,
                               QGroupBox, QLineEdit, QLabel, QMessageBox, QApplication, QHBoxLayout)
from PySide6.QtCore import Qt
from CORE.db_dataclasses import *
from DA3.redactors_widgets import BaseEditor
from DA3.redactors_widgets.pazzles_subwidgets import *
from DA3 import app_signals


class PCEditor(BaseEditor):
    """Редактор для HC объектов (работает ТОЛЬКО с полными классами)"""

    def __init__(self, parent: QWidget, form: Form, pc: BasePazzle,
                 classes_refs: List[BaseClass]):

        self._form = form  # Сохраняем форму для доступа к параметрам
        self._classes_refs = classes_refs
        super().__init__(parent, pc)
        self.setWindowTitle("Редактор PC объекта (parameter calculator)")



    def _create_form_widget(self) -> QWidget:
        """Создание виджета с полями ввода"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)  # Основное горизонтальное расположение
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Левый столбец
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Основные поля HC объекта
        group_box = QGroupBox("Параметры HC объекта")
        group_layout = QFormLayout(group_box)
        group_layout.setContentsMargins(15, 15, 15, 15)
        group_layout.setSpacing(10)
        group_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.id_label = QLabel(str(self.original_data.id) if self.original_data.id else "Новый")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя HC объекта")
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий")

        group_layout.addRow("ID:", self.id_label)
        group_layout.addRow("Имя:", self.name_edit)
        group_layout.addRow("Комментарий:", self.comment_edit)

        left_layout.addWidget(group_box)

        # Выбор класса
        class_group = QGroupBox("Выбор класса")
        class_layout = QVBoxLayout(class_group)
        class_layout.setContentsMargins(15, 15, 15, 15)

        self.classes_widget = ClassesListWidget(self._classes_refs)
        self.classes_widget.class_selected.connect(self._on_class_selected)
        class_layout.addWidget(self.classes_widget)
        left_layout.addWidget(class_group)

        # Выходные параметры
        self.output_params_widget = OutputParamsWidget()
        left_layout.addWidget(self.output_params_widget)

        left_layout.addStretch()  # Растягиваем вниз

        # Правый столбец
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # Аргументы конструктора
        self.arguments_widget = ArgumentsTableWidget()
        right_layout.addWidget(self.arguments_widget)

        # Входные параметры
        self.input_params_widget = InputParamsWidget()
        right_layout.addWidget(self.input_params_widget)

        # Входные точки
        self.input_points_widget = InputPointsWidget()
        right_layout.addWidget(self.input_points_widget)



        right_layout.addStretch()  # Растягиваем вниз

        # Добавляем колонки в основной макет
        main_layout.addWidget(left_column, 1)  # Вес 1 (растягиваются пропорционально)
        main_layout.addWidget(right_column, 1)  # Вес 1

        return widget

    def _load_data_to_ui(self) -> None:
        """Загрузка данных из HC объекта в интерфейс"""
        # Основные поля
        if self.original_data.name:
            self.name_edit.setText(self.original_data.name)
        if self.original_data.comment:
            self.comment_edit.setText(self.original_data.comment)

        self._load_class_ref()

        # Загружаем сохраненные значения аргументов
        self.arguments_widget.load_current_values(self.original_data.argument_values)

        # Загружаем сохраненные значения входных параметров
        self.input_params_widget.load_current_values(self.original_data.input_param_values)

        # Загружаем сохраненные значения выходных параметров
        self.output_params_widget.load_current_values(self.original_data.output_param_values)

        # Загружаем сохраненные значения входных точек
        self.input_points_widget.load_current_values(self.original_data.input_point_values)

    def _load_class_ref(self):
        if self.original_data.class_ref:
            self.classes_widget.set_selected_class(self.original_data.class_ref)

            # Загружаем сигнатуру аргументов
            self.arguments_widget.load_arguments(self.original_data.class_ref.constructor_arguments)

            # Загружаем сигнатуру входных параметров
            self.input_params_widget.load_input_params(
                self.original_data.class_ref.input_params,
                self._form.parameters
            )
            # Загружаем сигнатуру выходных параметров
            self.output_params_widget.load_output_params(
                self.original_data.class_ref.output_params,
                self._form.parameters
            )
            # Загружаем сигнатуру входных точек
            self.input_points_widget.load_input_points(
                self.original_data.class_ref.input_points,
                self._form.points
            )

    def _collect_data_from_ui(self) -> BasePazzle:
        """Сбор данных из интерфейса в объект"""
        updated_pc = BasePazzle()

        # Получаем основные поля
        updated_pc.id = self.original_data.id
        updated_pc.name = self.name_edit.text().strip() or None
        updated_pc.comment = self.comment_edit.text().strip()

        # Получаем сигнатуру класса
        updated_pc.class_ref = self.classes_widget.get_selected_class()

        # Получаем значения для аругметов конструктора
        updated_pc.argument_values = self.arguments_widget.get_argument_values()

        # Получаем значения входных параметров
        updated_pc.input_param_values = self.input_params_widget.get_input_param_values()

        # Получаем значения выходных параметров
        updated_pc.output_param_values = self.output_params_widget.get_output_param_values()

        # Получаем значения входных точек
        updated_pc.input_point_values = self.input_points_widget.get_input_point_values()

        return updated_pc

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        validators = [
            (self.classes_widget.get_selected_class, "Пожалуйста, выберите класс"),
            (self.input_params_widget.validate, self.input_params_widget.get_validation_errors),
            (self.output_params_widget.validate, self.output_params_widget.get_validation_errors),
            (self.input_points_widget.validate, self.input_points_widget.get_validation_errors)
        ]

        for validator, error_getter in validators:
            if not validator():
                error_msg = error_getter() if callable(error_getter) else error_getter
                QMessageBox.warning(self, "Ошибка", error_msg)
                return False

        return True


    def _emit_add_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала добавления нового объекта"""
        app_signals.base_pazzle.db_add_pc.emit(data)

    def _emit_update_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала обновления существующего HC объекта"""
        app_signals.base_pazzle.db_update_pazzle.emit(data)

    def _on_class_selected(self, selected_class: BaseClass):
        """Обработчик выбора класса"""
        # Загружаем аргументы конструктора
        self.arguments_widget.load_arguments(selected_class.constructor_arguments)

        # Загружаем входные параметры, используя параметры из формы
        self.input_params_widget.load_input_params(
            selected_class.input_params,
            self._form.parameters
        )

        # Загружаем входные параметры, используя параметры из формы
        self.output_params_widget.load_output_params(
            selected_class.output_params,
            self._form.parameters
        )

        # Загружаем входные точки, используя точки из формы
        self.input_points_widget.load_input_points(
            selected_class.input_points,
            self._form.points
        )


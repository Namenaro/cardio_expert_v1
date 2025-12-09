from typing import Optional, List
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout,
                               QGroupBox, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from CORE.db_dataclasses import BasePazzle, Form, BaseClass, Parameter
from DA3 import app_signals
from DA3.redactors_widgets import BaseEditor
from DA3.redactors_widgets.HC_editor.arguments_table_widget import ArgumentsTableWidget
from DA3.redactors_widgets.HC_editor.classes_list_widget import ClassesListWidget
from DA3.redactors_widgets.HC_editor.input_params_widget import InputParamsWidget


class HCEditor(BaseEditor):
    """Редактор для HC объектов (работает ТОЛЬКО с полными классами)"""

    def __init__(self, parent: QWidget, form: Form, hc: BasePazzle,
                 classes_refs: List[BaseClass]):
        self._form = form  # Сохраняем форму для доступа к параметрам
        self._classes_refs = classes_refs  # Гарантированно полные классы
        super().__init__(parent, hc)
        self.setWindowTitle("Редактор HC объекта")
        self.resize(600, 700)

    def _create_form_widget(self) -> QWidget:
        """Создание виджета с полями ввода"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

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
        layout.addWidget(group_box)

        # Выбор класса
        class_group = QGroupBox("Выбор класса")
        class_layout = QVBoxLayout(class_group)
        class_layout.setContentsMargins(15, 15, 15, 15)

        self.classes_widget = ClassesListWidget(self._classes_refs)
        self.classes_widget.class_selected.connect(self._on_class_selected)
        class_layout.addWidget(self.classes_widget)
        layout.addWidget(class_group)

        # Аргументы конструктора
        self.arguments_widget = ArgumentsTableWidget()
        layout.addWidget(self.arguments_widget)

        # Входные параметры
        self.input_params_widget = InputParamsWidget()
        layout.addWidget(self.input_params_widget)

        layout.addStretch()

        return widget

    def _on_class_selected(self, selected_class: BaseClass):
        """Обработчик выбора класса"""
        # Загружаем аргументы конструктора
        self.arguments_widget.load_arguments(selected_class.constructor_arguments)

        # Загружаем входные параметры, используя параметры из формы
        self.input_params_widget.load_input_params(
            selected_class.input_params,
            self._get_form_parameters()
        )

    def _get_form_parameters(self) -> List[Parameter]:
        """Получить параметры из текущей формы"""
        if self._form and hasattr(self._form, 'parameters'):
            return self._form.parameters
        return []

    def _load_data_to_ui(self) -> None:
        """Загрузка данных из HC объекта в интерфейс"""
        # Основные поля
        if self.original_data.name:
            self.name_edit.setText(self.original_data.name)
        if self.original_data.comment:
            self.comment_edit.setText(self.original_data.comment)

        # Находим полный класс в списке classes_refs
        if self.original_data.class_ref and self.original_data.class_ref.id:
            full_class = self._find_full_class(self.original_data.class_ref.id)
            if full_class:
                self.classes_widget.set_selected_class(full_class)
                self.arguments_widget.load_arguments(full_class.constructor_arguments)

                # Загружаем входные параметры класса
                self.input_params_widget.load_input_params(
                    full_class.input_params,
                    self._get_form_parameters()
                )

        # Загружаем сохраненные значения аргументов
        self._load_argument_values()

        # Загружаем сохраненные значения входных параметров
        self._load_input_param_values()

    def _load_input_param_values(self):
        """Загрузка значений входных параметров"""
        if hasattr(self.original_data, 'input_param_values') and self.original_data.input_param_values:
            self.input_params_widget.load_current_values(self.original_data.input_param_values)

    def _find_full_class(self, class_id: int) -> Optional[BaseClass]:
        """Найти полный класс по ID в списке classes_refs"""
        return next((c for c in self._classes_refs if c.id == class_id), None)

    def _load_argument_values(self):
        """Загрузка значений аргументов"""
        if not self.original_data.argument_values:
            return

        # Создаем словарь значений
        arg_values = {av.argument_id: av.argument_value
                      for av in self.original_data.argument_values if av.argument_id}

        # Устанавливаем значения в таблицу
        for row in range(self.arguments_widget.table_widget.rowCount()):
            if id_item := self.arguments_widget.table_widget.item(row, 0):
                if arg_id_str := id_item.text():
                    if arg_id := int(arg_id_str):
                        if value := arg_values.get(arg_id):
                            if value_item := self.arguments_widget.table_widget.item(row, 4):
                                value_item.setText(value)

    def _collect_data_from_ui(self) -> BasePazzle:
        """Сбор данных из интерфейса в объект"""
        updated_hc = BasePazzle()
        updated_hc.id = self.original_data.id
        updated_hc.name = self.name_edit.text().strip() or None
        updated_hc.comment = self.comment_edit.text().strip()
        updated_hc.class_ref = self.classes_widget.get_selected_class()
        updated_hc.argument_values = self.arguments_widget.get_argument_values()

        # Получаем значения входных параметров
        updated_hc.input_param_values = self.input_params_widget.get_input_param_values()

        # Копируем остальные поля
        for field in ['input_point_values', 'output_param_values']:
            if hasattr(self.original_data, field):
                setattr(updated_hc, field, getattr(self.original_data, field).copy())

        return updated_hc

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        # 1. Проверяем, что выбран класс
        if not self.classes_widget.get_selected_class():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите класс")
            return False

        # 2. Проверяем входные параметры через собственный валидатор виджета
        if not self.input_params_widget.validate():
            errors = self.input_params_widget.get_validation_errors()
            if errors:
                params_list = "\n• " + "\n• ".join(errors)
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Для следующих входных параметров класса необходимо выбрать параметры формы:\n{params_list}"
                )
            return False

        return True

    def _emit_add_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала добавления нового HC объекта"""
        app_signals.db_add_hc.emit(data)

    def _emit_update_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала обновления существующего HC объекта"""
        app_signals.db_update_object.emit(data)
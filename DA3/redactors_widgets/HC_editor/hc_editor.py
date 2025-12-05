from typing import Optional, List
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout,
                               QGroupBox, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from CORE.db_dataclasses import BasePazzle, Form, BaseClass
from DA3 import app_signals
from DA3.redactors_widgets import BaseEditor
from DA3.redactors_widgets.HC_editor.arguments_table_widget import ArgumentsTableWidget
from DA3.redactors_widgets.HC_editor.classes_list_widget import ClassesListWidget


class HCEditor(BaseEditor):
    """Редактор для HC объектов (работает ТОЛЬКО с полными классами)"""

    def __init__(self, parent: QWidget, form: Form, hc: BasePazzle,
                 classes_refs: List[BaseClass]):
        self._form = form
        self._classes_refs = classes_refs  # Гарантированно полные классы
        super().__init__(parent, hc)
        self.setWindowTitle("Редактор HC объекта")
        self.resize(600, 600)

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
        layout.addStretch()

        return widget

    def _on_class_selected(self, selected_class: BaseClass):
        """Обработчик выбора класса"""
        # selected_class гарантированно полный
        self.arguments_widget.load_arguments(selected_class.constructor_arguments)

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

        # Загружаем сохраненные значения аргументов
        self._load_argument_values()

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

        # Копируем остальные поля
        for field in ['input_param_values', 'input_point_values', 'output_param_values']:
            if hasattr(self.original_data, field):
                setattr(updated_hc, field, getattr(self.original_data, field).copy())

        return updated_hc

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        if not self.classes_widget.get_selected_class():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите класс")
            return False
        return True

    def _emit_add_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала добавления нового HC объекта"""
        app_signals.db_add_hc.emit(data)

    def _emit_update_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала обновления существующего HC объекта"""
        app_signals.db_update_object.emit(data)
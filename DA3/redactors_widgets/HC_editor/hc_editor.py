from typing import Optional, List
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QFormLayout, QGroupBox, QComboBox, QWidget, QMessageBox, QVBoxLayout
)
from PySide6.QtCore import Qt
from CORE.db_dataclasses import BasePazzle, Form, BaseClass
from DA3 import app_signals
from DA3.redactors_widgets import BaseEditor
from DA3.redactors_widgets.HC_editor.arguments_table_widget import ArgumentsTableWidget
from DA3.redactors_widgets.HC_editor.classes_list_widget import ClassesListWidget


class HCEditor(BaseEditor):
    """Редактор для HC объектов"""

    def __init__(self, parent: QWidget, form: Form, hc: BasePazzle, classes_refs: Optional[List[BaseClass]] = None):
        # Сохраняем дополнительные параметры как приватные поля
        self._form = form
        self._classes_refs = classes_refs or []

        # Проверяем классы на наличие аргументов без ID
        for class_ref in self._classes_refs:
            if hasattr(class_ref, 'constructor_arguments'):
                for arg in class_ref.constructor_arguments:
                    if arg.id is None:
                        print(f"ВНИМАНИЕ: Класс {class_ref.name} содержит аргумент без ID: {arg.name}")

        # Передаем hc как data_object в родительский класс
        super().__init__(parent, hc)

        # Настраиваем окно
        self.setWindowTitle("Редактор HC объекта")
        self.resize(600, 600)

    def _create_form_widget(self) -> QWidget:
        """Создание виджета с полями ввода для HC"""
        form_widget = QWidget()
        layout = QVBoxLayout(form_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Группа основных полей HC объекта
        group_box = QGroupBox("Параметры HC объекта")
        group_layout = QFormLayout(group_box)
        group_layout.setContentsMargins(15, 15, 15, 15)
        group_layout.setSpacing(10)
        group_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # ID (нередактируемое)
        self.id_label = QLabel(str(self.original_data.id) if self.original_data.id else "Новый")
        group_layout.addRow("ID:", self.id_label)

        # Поле для имени
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя HC объекта")
        group_layout.addRow("Имя:", self.name_edit)

        # Поле для комментария
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий")
        group_layout.addRow("Комментарий:", self.comment_edit)

        layout.addWidget(group_box)

        # Виджет выбора класса
        class_group = QGroupBox("Выбор класса")
        class_layout = QVBoxLayout(class_group)
        class_layout.setContentsMargins(15, 15, 15, 15)

        # Информационная метка
        info_label = QLabel("Выберите класс из списка ниже:")
        info_label.setStyleSheet("font-style: italic; color: #666;")
        class_layout.addWidget(info_label)

        # Виджет списка классов
        self.classes_widget = ClassesListWidget(self._classes_refs)
        self.classes_widget.class_selected.connect(self.on_class_selected)
        class_layout.addWidget(self.classes_widget)

        layout.addWidget(class_group)

        # Виджет аргументов конструктора
        self.arguments_widget = ArgumentsTableWidget()
        layout.addWidget(self.arguments_widget)

        layout.addStretch()

        return form_widget

    def on_class_selected(self, selected_class: BaseClass):
        """Обработчик выбора класса"""
        if selected_class and hasattr(selected_class, 'constructor_arguments'):
            # Загружаем аргументы конструктора в таблицу
            self.arguments_widget.load_arguments(selected_class.constructor_arguments)
        else:
            self.arguments_widget.clear()

    def _set_current_class(self):
        """Установка текущего класса в виджете выбора"""
        current_class = self.original_data.class_ref
        self.classes_widget.set_selected_class(current_class)

        # Загружаем аргументы текущего класса
        if current_class and hasattr(current_class, 'constructor_arguments'):
            self.arguments_widget.load_arguments(current_class.constructor_arguments)

    def _load_data_to_ui(self) -> None:
        """Загрузка данных из HC объекта в интерфейс"""
        if self.original_data.name:
            self.name_edit.setText(self.original_data.name)

        if self.original_data.comment:
            self.comment_edit.setText(self.original_data.comment)

        # Устанавливаем текущий класс
        self._set_current_class()

        # Заполняем значения аргументов из существующего объекта
        self._load_argument_values()

    def _load_argument_values(self):
        """Загрузка значений аргументов из существующего объекта в таблицу"""
        if not self.original_data.argument_values or not self.original_data.class_ref:
            return

        # Создаем словарь значений аргументов для быстрого поиска по argument_id
        arg_values_map = {}
        for arg_value in self.original_data.argument_values:
            if arg_value.argument_id:
                arg_values_map[arg_value.argument_id] = arg_value.argument_value

        # Устанавливаем значения в таблицу
        for row in range(self.arguments_widget.table_widget.rowCount()):
            id_item = self.arguments_widget.table_widget.item(row, 0)
            if id_item and id_item.text():
                try:
                    arg_id = int(id_item.text())
                    if arg_id in arg_values_map:
                        value_item = self.arguments_widget.table_widget.item(row, 4)
                        if value_item:
                            value_item.setText(arg_values_map[arg_id])
                except ValueError:
                    continue

    def _collect_data_from_ui(self) -> BasePazzle:
        """Сбор данных из интерфейса в объект"""
        # Создаем копию оригинального объекта с обновленными данными
        updated_hc = BasePazzle()

        # Сохраняем ID (если был)
        updated_hc.id = self.original_data.id

        # Забираем данные из полей
        updated_hc.name = self.name_edit.text().strip() or None
        updated_hc.comment = self.comment_edit.text().strip()

        # Забираем выбранный класс
        updated_hc.class_ref = self.classes_widget.get_selected_class()

        # Забираем значения аргументов из таблицы
        # Метод get_argument_values() уже устанавливает правильный argument_id
        updated_hc.argument_values = self.arguments_widget.get_argument_values()

        # Копируем остальные поля из оригинала
        updated_hc.input_param_values = self.original_data.input_param_values.copy()
        updated_hc.input_point_values = self.original_data.input_point_values.copy()
        updated_hc.output_param_values = self.original_data.output_param_values.copy()

        return updated_hc

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        # Проверяем, что выбран класс
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
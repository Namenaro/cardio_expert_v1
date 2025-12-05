from typing import Optional, List
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QFormLayout, QGroupBox, QWidget
)
from PySide6.QtCore import Qt
from CORE.db_dataclasses import BasePazzle, Form
from DA3 import app_signals
from DA3.redactors_widgets import BaseEditor


class HCEditor(BaseEditor):
    """Редактор для HC объектов"""

    def __init__(self, parent: QWidget, form: Form, hc: BasePazzle, classes_refs: Optional[List] = None):
        # Сохраняем дополнительные параметры как приватные поля
        self._form = form
        self._classes_refs = classes_refs

        # Передаем hc как data_object в родительский класс
        super().__init__(parent, hc)

        # Настраиваем окно
        self.setWindowTitle("Редактор HC объекта")
        self.resize(400, 200)

    def _create_form_widget(self) -> QWidget:
        """Создание виджета с полями ввода для HC"""
        form_widget = QWidget()
        layout = QFormLayout(form_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Группа основных полей
        group_box = QGroupBox("Основные параметры")
        group_layout = QFormLayout(group_box)
        group_layout.setContentsMargins(15, 15, 15, 15)
        group_layout.setSpacing(10)

        # ID (нередактируемое)
        self.id_label = QLabel(str(self.original_data.id) if self.original_data.id else "Новый")
        group_layout.addRow("ID:", self.id_label)

        # Поле для имени
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя HC объекта")
        self.name_edit.setMaximumWidth(300)
        group_layout.addRow("Имя:", self.name_edit)

        # Поле для комментария
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий")
        self.comment_edit.setMaximumWidth(300)
        group_layout.addRow("Комментарий:", self.comment_edit)

        layout.addWidget(group_box)

        return form_widget

    def _load_data_to_ui(self) -> None:
        """Загрузка данных из HC объекта в интерфейс"""
        if self.original_data.name:
            self.name_edit.setText(self.original_data.name)

        if self.original_data.comment:
            self.comment_edit.setText(self.original_data.comment)

    def _collect_data_from_ui(self) -> BasePazzle:
        """Сбор данных из интерфейса в объект"""
        # Создаем копию оригинального объекта с обновленными данными
        updated_hc = BasePazzle()

        # Сохраняем ID (если был)
        updated_hc.id = self.original_data.id

        # Забираем данные из полей
        updated_hc.name = self.name_edit.text().strip() or None
        updated_hc.comment = self.comment_edit.text().strip()

        # Копируем остальные поля из оригинала
        updated_hc.class_ref = self.original_data.class_ref
        updated_hc.argument_values = self.original_data.argument_values.copy()
        updated_hc.input_param_values = self.original_data.input_param_values.copy()
        updated_hc.input_point_values = self.original_data.input_point_values.copy()
        updated_hc.output_param_values = self.original_data.output_param_values.copy()

        return updated_hc

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        # Имя может быть пустым (NULL в БД), поэтому всегда возвращаем True
        return True

    def _emit_add_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала добавления нового HC объекта"""
        app_signals.db_add_hc.emit(data)

    def _emit_update_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала обновления существующего HC объекта"""
        app_signals.db_update_object.emit(data)
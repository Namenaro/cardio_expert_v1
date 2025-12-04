from copy import deepcopy
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit
)
from DA3.redactors_widgets.base_editor import BaseEditor
from DA3 import app_signals
from CORE.db_dataclasses import Parameter


class ParameterEditor(BaseEditor):
    """Редактор параметра"""

    def __init__(self, parent: QWidget, parameter: Parameter):
        super().__init__(parent, parameter)
        self.setWindowTitle("Редактирование параметра")
        self.resize(400, 300)

    def _create_form_widget(self) -> QWidget:
        """Создание виджета с полями параметра"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # ID параметра
        self._add_id_field(layout, "ID параметра")

        # Название параметра
        name_label = QLabel("Название параметра*:")
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название параметра")
        layout.addWidget(self.name_edit)

        # Комментарий
        comment_label = QLabel("Комментарий:")
        comment_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(comment_label)

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий к параметру")
        self.comment_edit.setMaximumHeight(100)
        layout.addWidget(self.comment_edit)

        layout.addStretch()
        return widget

    def _add_id_field(self, layout: QVBoxLayout, label_text: str) -> None:
        """Добавление поля ID"""
        id_layout = QHBoxLayout()
        id_label = QLabel(f"{label_text}:")
        id_label.setStyleSheet("font-weight: bold;")
        id_layout.addWidget(id_label)

        id_value = str(self.original_data.id) if self.original_data.id is not None else "Новая"
        self.id_label = QLabel(id_value)
        self.id_label.setStyleSheet("color: #666;")
        id_layout.addWidget(self.id_label)
        id_layout.addStretch()
        layout.addLayout(id_layout)

    def _load_data_to_ui(self) -> None:
        """Загрузка данных в интерфейс"""
        self.name_edit.setText(self.original_data.name)
        self.comment_edit.setPlainText(self.original_data.comment)

    def _collect_data_from_ui(self) -> Parameter:
        """Сбор данных из интерфейса"""
        # Создаем глубокую копию оригинального параметра
        param_copy = deepcopy(self.original_data)

        # Обновляем поля из интерфейса
        param_copy.name = self.name_edit.text().strip()
        param_copy.comment = self.comment_edit.toPlainText().strip()

        return param_copy

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        return bool(self.name_edit.text().strip())

    def _emit_add_signal(self, param_data: Parameter) -> None:
        """Испускание сигнала добавления нового параметра"""
        app_signals.db_add_parameter.emit(param_data)

    def _emit_update_signal(self, param_data: Parameter) -> None:
        """Испускание сигнала обновления параметра"""
        app_signals.db_update_object.emit(param_data)
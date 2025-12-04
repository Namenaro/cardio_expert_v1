from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit
)
from DA3.redactors_widgets.base_editor import BaseEditor
from DA3 import app_signals
from CORE.db_dataclasses import Point
from copy import deepcopy


class PointEditor(BaseEditor):
    """Редактор точки"""

    def __init__(self, parent: QWidget, point: Point):
        super().__init__(parent, point)
        self.setWindowTitle("Редактирование точки")
        self.resize(400, 300)

    def _create_form_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # ID точки
        self._add_id_field(layout, "ID точки")

        # Имя точки
        name_label = QLabel("Имя точки*:")
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя точки")
        layout.addWidget(self.name_edit)

        # Комментарий
        comment_label = QLabel("Комментарий:")
        comment_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(comment_label)

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий к точке")
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
        # Загружаем данные из оригинального объекта
        self.name_edit.setText(self.original_data.name)
        self.comment_edit.setText(self.original_data.comment)

    def _collect_data_from_ui(self) -> Point:
        """Сбор данных из интерфейса"""
        # Создаем глубокую копию оригинальной точки
        point_copy = deepcopy(self.original_data)

        # Обновляем только поля, которые редактируются в интерфейсе
        point_copy.name = self.name_edit.text().strip()
        point_copy.comment = self.comment_edit.toPlainText().strip()

        return point_copy

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        return bool(self.name_edit.text().strip())

    def _emit_add_signal(self, point_data: Point) -> None:
        """Испускание сигнала добавления новой точки"""
        app_signals.db_add_point.emit(point_data)

    def _emit_update_signal(self, point_data: Point) -> None:
        """Испускание сигнала обновления точки"""
        app_signals.db_update_object.emit(point_data)
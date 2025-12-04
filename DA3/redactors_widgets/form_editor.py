from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog
)
from DA3.redactors_widgets.base_editor import BaseEditor
from DA3 import app_signals
from CORE.db_dataclasses import Form
from copy import deepcopy


class FormEditor(BaseEditor):
    """Редактор основной информации о форме"""

    def __init__(self, parent: QWidget, form: Form):
        super().__init__(parent, form)
        self.setWindowTitle("Редактирование основной информации формы")
        self.resize(500, 400)

    def _create_form_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # ID формы
        self._add_id_field(layout, "ID формы")

        # Название формы
        name_label = QLabel("Название формы*:")
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название формы")
        layout.addWidget(self.name_edit)

        # Комментарий
        comment_label = QLabel("Комментарий:")
        comment_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(comment_label)

        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий к форме")
        self.comment_edit.setMaximumHeight(100)
        layout.addWidget(self.comment_edit)

        # Путь к картинке
        image_label = QLabel("Путь к картинке:")
        image_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(image_label)

        image_layout = QHBoxLayout()
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("Выберите файл изображения")
        self.image_path_edit.setReadOnly(True)
        image_layout.addWidget(self.image_path_edit)

        self.browse_image_button = QPushButton("Обзор...")
        self.browse_image_button.clicked.connect(self._browse_image)
        image_layout.addWidget(self.browse_image_button)
        layout.addLayout(image_layout)

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

    def _browse_image(self) -> None:
        """Открытие диалога выбора файла изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.gif);;Все файлы (*.*)"
        )

        if file_path:
            self.image_path_edit.setText(file_path)

    def _load_data_to_ui(self) -> None:
        """Загрузка данных в интерфейс"""
        # Загружаем данные из оригинального объекта
        self.name_edit.setText(self.original_data.name)
        self.comment_edit.setText(self.original_data.comment)

        if self.original_data.path_to_pic:
            self.image_path_edit.setText(self.original_data.path_to_pic)

    def _collect_data_from_ui(self) -> Form:
        """Сбор данных из интерфейса"""
        # Создаем глубокую копию оригинальной формы
        form_copy = deepcopy(self.original_data)

        # Обновляем только поля, которые редактируются в интерфейсе
        form_copy.name = self.name_edit.text().strip()
        form_copy.comment = self.comment_edit.toPlainText().strip()
        form_copy.path_to_pic = self.image_path_edit.text().strip()

        return form_copy

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        return bool(self.name_edit.text().strip())

    def _emit_add_signal(self, form_data: Form) -> None:
        """Испускание сигнала добавления новой формы"""
        app_signals.db_add_form.emit(form_data)

    def _emit_update_signal(self, form_data: Form) -> None:
        """Испускание сигнала обновления формы"""
        app_signals.db_update_object.emit(form_data)
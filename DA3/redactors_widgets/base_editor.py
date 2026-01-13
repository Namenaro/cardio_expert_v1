from abc import ABC, abstractmethod
from typing import Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QMessageBox, QWidget, QApplication
)
from PySide6.QtCore import Signal, Qt


class BaseEditor(QDialog):
    """Базовый класс для редакторов объектов с ID"""

    # Сигнал для закрытия редактора
    editor_closed = Signal()

    def __init__(self, parent: QWidget, data_object: Any):
        super().__init__(parent)
        self.original_data = data_object  # Сохраняем ссылку на оригинальный объект для сравнения на наличие изменений при сохранении.
        self.setModal(True)
        # Устанавливаем адаптивный размер (70% от экрана)
        screen = QApplication.primaryScreen().size()
        width = int(screen.width() * 0.7)
        height = int(screen.height() * 0.7)
        self.resize(width, height)

        # Устанавливаем стандартные флаги окна (свернуть, развернуть, закрыть)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.setup_ui()

    def setup_ui(self) -> None:
        """Базовая настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Основная часть с полями ввода
        self.form_widget = self._create_form_widget()
        layout.addWidget(self.form_widget)

        # Кнопки действий
        self._create_action_buttons(layout)

        # Загрузка данных в UI
        self._load_data_to_ui()

    def _create_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Создание кнопок действий"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        parent_layout.addLayout(button_layout)


    def _create_form_widget(self) -> QWidget:
        """Создание виджета с полями ввода"""
        raise NotImplementedError


    def _load_data_to_ui(self) -> None:
        """Загрузка данных из объекта в интерфейс"""
        raise NotImplementedError


    def _collect_data_from_ui(self) -> Any:
        """Сбор данных из интерфейса в объект"""
        raise NotImplementedError


    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        raise NotImplementedError


    def _emit_add_signal(self, data: Any) -> None:
        """Испускание сигнала добавления нового объекта"""
        raise NotImplementedError


    def _emit_update_signal(self, data: Any) -> None:
        """Испускание сигнала обновления существующего объекта"""
        raise NotImplementedError

    def _on_save_clicked(self) -> None:
        """Обработчик нажатия кнопки сохранения"""
        if not self._validate_data():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля")
            return

        # Собираем данные из интерфейса в новый объект
        updated_data = self._collect_data_from_ui()

        # Испускаем соответствующий сигнал
        if self._is_new_object():
            self._emit_add_signal(updated_data)
        else:
            self._emit_update_signal(updated_data)

        # Закрываем редактор
        self.accept()
        self.editor_closed.emit()

    def _on_cancel_clicked(self) -> None:
        """Обработчик нажатия кнопки отмены"""
        # Проверяем, были ли изменения
        if self._has_changes():
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Изменения не будут сохранены. Продолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

        self.reject()
        self.editor_closed.emit()

    def _has_changes(self) -> bool:
        """Проверка, были ли изменения"""
        # Собираем текущие данные из UI
        current_data = self._collect_data_from_ui()

        # Сравниваем текущие данные с оригинальными
        return current_data != self.original_data

    def _is_new_object(self) -> bool:
        """Проверка, является ли объект новым (не сохраненным в БД)"""
        return self.original_data is None or self.original_data.id is None

    def closeEvent(self, event: Any) -> None:
        """Обработчик закрытия окна"""
        self._on_cancel_clicked()
        event.ignore()
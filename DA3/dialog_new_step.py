from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QHBoxLayout, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from dataclasses import field
from typing import List, Optional

from DA3 import app_signals
from CORE.db_dataclasses import Step, Point



class AddStepDialog(QDialog):
    def __init__(self, points: List[Point], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить шаг")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.resize(400, 200)

        self._points = points
        self._step: Optional[Step] = None

        self._setup_ui()
        self._populate_points()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        # Поле ввода номера шага в форме
        self._num_in_form_edit = QLineEdit()
        form_layout.addRow("Номер шага в форме:", self._num_in_form_edit)

        # Выпадающий список для выбора целевой точки
        self._target_point_combo = QComboBox()
        form_layout.addRow("Целевая точка (ID):", self._target_point_combo)

        # Поле ввода комментария
        self._comment_edit = QLineEdit()
        form_layout.addRow("Комментарий:", self._comment_edit)

        # Кнопки
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)

        self._create_btn = QPushButton("Создать")
        self._create_btn.clicked.connect(self._on_create_clicked)
        buttons_layout.addWidget(self._create_btn)

        self._cancel_btn = QPushButton("Отмена")
        self._cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_btn)

    def _populate_points(self):
        """Заполняет комбобокс списком точек (по ID)."""
        for point in self._points:
            display_text = f"{point.id} — {point.name}"
            self._target_point_combo.addItem(display_text, point)

    def _on_create_clicked(self):
        """Обработчик нажатия кнопки «Создать»."""
        # Проверка и получение номера шага
        try:
            num_text = self._num_in_form_edit.text().strip()
            if not num_text:
                raise ValueError("Номер шага не может быть пустым.")
            num_in_form = int(num_text)
            if num_in_form < 0:
                raise ValueError("Номер шага должен быть неотрицательным целым числом.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return

        # Получение целевой точки из комбобокса
        point_index = self._target_point_combo.currentIndex()
        if point_index == -1:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать целевую точку.")
            return
        target_point = self._target_point_combo.currentData()

        # Получение комментария
        comment = self._comment_edit.text().strip()

        # Создаем экземпляр Step
        self._step = Step(
            num_in_form=num_in_form,
            target_point=target_point,
            comment=comment
        )

        # Эмитируем сигнал и закрываем диалог
        app_signals.db_add_step.emit(self._step)
        self.accept()



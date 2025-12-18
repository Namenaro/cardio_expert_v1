from CORE.db_dataclasses import *
from DA3 import app_signals
from dataclasses import dataclass, field
from typing import Optional, List
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QFormLayout, QLabel, QPushButton, QApplication, QHBoxLayout, QWidget
)
from PySide6.QtCore import Qt

class StepInfoCard(QFrame):
    def __init__(self, step: Step, parent=None):
        super().__init__(parent)
        self.step = step
        self.setup_ui()

    def setup_ui(self):
        # Основной макет
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Форма для отображения данных
        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        # Комментарий
        self.comment_label = QLabel()
        self.comment_label.setText(self.step.comment)
        form_layout.addRow("Комментарий:", self.comment_label)

        # Порядковый номер шага
        self.num_label = QLabel()
        self.num_label.setNum(self.step.num_in_form)
        form_layout.addRow("Номер в форме:", self.num_label)

        # Количество треков
        self.tracks_count_label = QLabel()
        self.tracks_count_label.setNum(len(self.step.tracks))
        form_layout.addRow("Количество треков:", self.tracks_count_label)

        # left_padding_t
        self.left_padding_label = QLabel()
        if self.step.left_padding_t is not None:
            self.left_padding_label.setText(f"{self.step.left_padding_t}")
        form_layout.addRow("Левый отступ (t):", self.left_padding_label)

        # right_padding_t
        self.right_padding_label = QLabel()
        if self.step.right_padding_t is not None:
            self.right_padding_label.setText(f"{self.step.right_padding_t}")
        form_layout.addRow("Правый отступ (t):", self.right_padding_label)

        # id
        self.id_label = QLabel()
        if self.step.id is not None:
            self.id_label.setNum(self.step.id)
        form_layout.addRow("ID:", self.id_label)

        # target_point name
        self.target_point_name_label = QLabel()
        if self.step.target_point is not None:
            self.target_point_name_label.setText(self.step.target_point.name)
        form_layout.addRow("Целевая точка:", self.target_point_name_label)

        # left_point name
        self.left_point_name_label = QLabel()
        if self.step.left_point is not None:
            self.left_point_name_label.setText(self.step.left_point.name)
        form_layout.addRow("Левая точка:", self.left_point_name_label)

        # right_point name
        self.right_point_name_label = QLabel()
        if self.step.right_point is not None:
            self.right_point_name_label.setText(self.step.right_point.name)
        form_layout.addRow("Правая точка:", self.right_point_name_label)

        # Контейнер для кнопок (горизонтальный макет)
        buttons_layout = QHBoxLayout()

        # Кнопка "редактировать"
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.edit_button)

        # Контейнер для кнопок (горизонтальный макет)
        buttons_layout = QHBoxLayout()

        # Добавляем растяжимый пробел слева → кнопки «прижмутся» вправо
        buttons_layout.addStretch()

        # Кнопка "редактировать"
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.edit_button)

        # Кнопка "удалить шаг"
        self.delete_button = QPushButton("Удалить шаг")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.delete_button)

        # Добавляем горизонтальный макет прямо в основной (без контейнера)
        layout.addLayout(buttons_layout)


    def on_edit_clicked(self):
        print("Кнопка 'Редактировать' нажата. Реализация пока отсутствует.")

    def on_delete_clicked(self):
        app_signals.db_delete_object.emit(self.step)


# Mock-тестирование
if __name__ == "__main__":
    import sys

    # Создаем mock-данные для тестирования
    point1 = Point(name="Точка A")
    point2 = Point(name="Точка B")
    point3 = Point(name="Точка C")

    track1 = Track()
    track2 = Track()

    step = Step(
        num_in_form=1,
        target_point=point1,
        id=101,
        tracks=[track1, track2],
        right_point=point2,
        left_point=point3,
        left_padding_t=0.5,
        right_padding_t=1.2,
        comment="Пример комментария для шага"
    )

    # Инициализируем приложение
    app = QApplication(sys.argv)

    # Создаем и показываем виджет
    widget = StepInfoCard(step)
    widget.setWindowTitle("StepInfoCard Test")
    widget.resize(400, 300)
    widget.show()

    sys.exit(app.exec())
from CORE.db_dataclasses import *
from DA3 import app_signals
from typing import List
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QFormLayout, QLabel, QPushButton, QApplication,
    QHBoxLayout, QSizePolicy, QWidget, QScrollArea
)
from PySide6.QtCore import Qt
import logging

from DA3.base_widget import BaseWidget


class StepInfoCard(BaseWidget):
    def __init__(self, step: Step, parent=None):
        super().__init__(parent)
        self.step = step
        self.setup_ui()
        self.apply_styles("step_info_card.qss")

    def setup_ui(self):
        # Основной вертикальный макет
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Область прокрутки для формы
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        main_layout.addWidget(scroll)

        # Контейнер для содержимого
        container = QWidget()
        scroll.setWidget(container)

        form_layout = QFormLayout(container)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(8)
        form_layout.setContentsMargins(12, 12, 12, 12)

        # ID
        self.id_label = QLabel()
        if self.step.id is not None:
            self.id_label.setNum(self.step.id)
        else:
            self.id_label.setText("—")
        self.id_label.setObjectName("idLabel")  # Метка для CSS
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.id_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)

        form_layout.addRow(self.id_label)
        form_layout.setWidget(form_layout.rowCount() - 1, QFormLayout.FieldRole, self.id_label)

        # Целевая точка
        self.target_point_name_label = QLabel()
        self.target_point_name_label.setWordWrap(True)
        self.target_point_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if self.step.target_point is not None:
            self.target_point_name_label.setText(self.step.target_point.name)
        else:
            self.target_point_name_label.setText("Не задано")
        form_layout.addRow("Целевая точка:", self.target_point_name_label)

        # Порядковый номер шага
        self.num_label = QLabel()
        self.num_label.setNum(self.step.num_in_form)
        form_layout.addRow("Номер в форме:", self.num_label)

        # Комментарий
        self.comment_label = QLabel()
        self.comment_label.setWordWrap(True)
        self.comment_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.comment_label.setText(self.step.comment or "")
        form_layout.addRow("Комментарий:", self.comment_label)

        # Горизонтальная линия
        line1 = QFrame()
        line1.setProperty("class", "separator")  # Метка для CSS
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_layout.addRow(line1)

        # Подпись "Ограничение слева"
        limit_left_label = QLabel("<b>Ограничение слева</b>")
        limit_left_label.setProperty("class", "sectionLabel")  # Метка для CSS
        limit_left_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        form_layout.addRow(limit_left_label)

        # Левое ограничение - показываем только то, что задано
        left_point_set = self.step.left_point is not None
        left_padding_set = self.step.left_padding_t is not None

        if left_point_set and not left_padding_set:
            # Только левая точка
            self.left_point_name_label = QLabel()
            self.left_point_name_label.setWordWrap(True)
            self.left_point_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.left_point_name_label.setText(self.step.left_point.name)
            form_layout.addRow("Левая точка:", self.left_point_name_label)
        elif left_padding_set and not left_point_set:
            # Только левый отступ
            self.left_padding_label = QLabel()
            self.left_padding_label.setText(f"{self.step.left_padding_t}")
            form_layout.addRow("Левый отступ (t):", self.left_padding_label)
        elif left_point_set and left_padding_set:
            # Оба поля заданы - показываем оба
            self.left_point_name_label = QLabel()
            self.left_point_name_label.setWordWrap(True)
            self.left_point_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.left_point_name_label.setText(self.step.left_point.name)
            form_layout.addRow("Левая точка:", self.left_point_name_label)

            self.left_padding_label = QLabel()
            self.left_padding_label.setText(f"{self.step.left_padding_t}")
            form_layout.addRow("Левый отступ (t):", self.left_padding_label)
        else:
            # Ничего не задано
            nothing_label = QLabel("Не задано")
            nothing_label.setStyleSheet("color: gray; font-style: italic;")
            form_layout.addRow("Левое ограничение:", nothing_label)

        # Вторая горизонтальная линия
        line2 = QFrame()
        line2.setProperty("class", "separator")  # Метка для CSS
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_layout.addRow(line2)

        # Подпись "Ограничение справа"
        limit_right_label = QLabel("<b>Ограничение справа</b>")
        limit_right_label.setProperty("class", "sectionLabel")  # Метка для CSS
        limit_right_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        form_layout.addRow(limit_right_label)

        # Правое ограничение - показываем только то, что задано
        right_point_set = self.step.right_point is not None
        right_padding_set = self.step.right_padding_t is not None

        if right_point_set and not right_padding_set:
            # Только правая точка
            self.right_point_name_label = QLabel()
            self.right_point_name_label.setWordWrap(True)
            self.right_point_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.right_point_name_label.setText(self.step.right_point.name)
            form_layout.addRow("Правая точка:", self.right_point_name_label)
        elif right_padding_set and not right_point_set:
            # Только правый отступ
            self.right_padding_label = QLabel()
            self.right_padding_label.setText(f"{self.step.right_padding_t}")
            form_layout.addRow("Правый отступ (t):", self.right_padding_label)
        elif right_point_set and right_padding_set:
            # Оба поля заданы - показываем оба
            self.right_point_name_label = QLabel()
            self.right_point_name_label.setWordWrap(True)
            self.right_point_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.right_point_name_label.setText(self.step.right_point.name)
            form_layout.addRow("Правая точка:", self.right_point_name_label)

            self.right_padding_label = QLabel()
            self.right_padding_label.setText(f"{self.step.right_padding_t}")
            form_layout.addRow("Правый отступ (t):", self.right_padding_label)
        else:
            # Ничего не задано
            nothing_label = QLabel("Не задано")
            nothing_label.setStyleSheet("color: gray; font-style: italic;")
            form_layout.addRow("Правое ограничение:", nothing_label)

        # Контейнер для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(12, 8, 12, 12)
        buttons_layout.addStretch()

        self.edit_button = QPushButton("Редактировать шаг")
        self.edit_button.setObjectName("editButton")  # Метка для CSS
        self.edit_button.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить шаг")
        self.delete_button.setObjectName("deleteButton")  # Метка для CSS
        self.delete_button.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.delete_button)

        main_layout.addLayout(buttons_layout)

    def on_edit_clicked(self):
        logging.info(f"Запуск редактора основной информации о шаге {self.step.id}")
        app_signals.step.request_step_info_redactor.emit(self.step)

    def on_delete_clicked(self):
        app_signals.step.db_delete_step.emit(self.step)


# тестирование
if __name__ == "__main__":
    import sys

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

    app = QApplication(sys.argv)
    widget = StepInfoCard(step)
    widget.setWindowTitle("StepInfoCard Test")
    widget.resize(400, 500)
    widget.show()
    sys.exit(app.exec())
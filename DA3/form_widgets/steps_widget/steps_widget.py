from typing import List, Optional
from dataclasses import dataclass
from PySide6.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt

from DA3.form_widgets.steps_widget.step_card import StepCard
from DA3.form_widgets.steps_widget.track_card import TrackCard
from DA3.form_widgets.steps_widget.step_info_card import StepInfoCard
from CORE.db_dataclasses import Step, Point


from DA3.form_widgets.steps_widget.track_card import TrackCard
from DA3.form_widgets.steps_widget.step_info_card import StepInfoCard
from CORE.db_dataclasses import *

from typing import List, Optional
from dataclasses import field
from PySide6.QtWidgets import (
    QTabWidget, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QFrame, QApplication
)
from PySide6.QtCore import Qt



class StepsWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._steps: Optional[List[Step]] = None
        self.setMovable(False)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget, 1)

        button_layout = QHBoxLayout()
        self.btn_add_step = QPushButton("Добавить шаг")
        self.btn_add_step.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Зелёный */
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_add_step.clicked.connect(self.on_add_step_clicked)
        button_layout.addWidget(self.btn_add_step)

        self.btn_remove_step = QPushButton("Удалить шаг")
        self.btn_remove_step.setStyleSheet("""
            QPushButton {
                background-color: #f44336;  /* Красный */
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_remove_step.clicked.connect(self.on_remove_step_clicked)
        button_layout.addWidget(self.btn_remove_step)

        main_layout.addLayout(button_layout)

    def reset_steps(self, steps: List[Step]) -> None:
        self._steps = steps
        self.refresh()

    def refresh(self) -> None:
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)

        if not self._steps:
            return

        sorted_steps = sorted(self._steps, key=lambda s: s.num_in_form)
        for step in sorted_steps:
            target_point_name = step.target_point.name if step.target_point else "Не задано"
            tab_title = f"{step.num_in_form}. {target_point_name}"
            step_card = StepCard(step)
            self.tab_widget.addTab(step_card, tab_title)

    def on_add_step_clicked(self):
        print("Кнопка 'Добавить шаг' нажата. Реализация пока отсутствует.")

    def on_remove_step_clicked(self):
        print("Кнопка 'Удалить шаг' нажата. Реализация пока отсутствует.")






# Mock-тестирование
if __name__ == "__main__":
    import sys

    # Создаем mock-данные для тестирования
    point1 = Point(name="Целевая точка 1")
    point2 = Point(name="Левая точка 1")
    point3 = Point(name="Правая точка 1")

    point4 = Point(name="Целевая точка 2")
    point5 = Point(name="Левая точка 2")
    point6 = Point(name="Правая точка 2")

    pazzle1 = BasePazzle()
    pazzle2 = BasePazzle()
    pazzle3 = BasePazzle()

    track1 = Track(
        id=101,
        SMs=[pazzle1, pazzle2],
        PSs=[pazzle3]
    )
    track2 = Track(
        id=102,
        SMs=[pazzle1],
        PSs=[pazzle2, pazzle3]
    )
    track3 = Track(
        id=103,
        SMs=[pazzle2],
        PSs=[pazzle1, pazzle3]
    )

    step1 = Step(
        num_in_form=1,
        target_point=point1,
        id=1,
        tracks=[track1, track2],
        right_point=point3,
        left_point=point2,
        left_padding_t=0.5,
        right_padding_t=1.2,
        comment="Комментарий для шага 1"
    )

    step2 = Step(
        num_in_form=2,
        target_point=point4,
        id=2,
        tracks=[track3],
        right_point=point6,
        left_point=point5,
        left_padding_t=0.8,
        right_padding_t=1.5,
        comment="Комментарий для шага 2"
    )

    steps = [step1, step2]

    # Инициализируем приложение
    app = QApplication(sys.argv)

    # Создаем и показываем виджет StepsWidget
    widget = StepsWidget()
    widget.reset_steps(steps)
    widget.setWindowTitle("StepsWidget Test")
    widget.resize(1000, 700)
    widget.show()

    sys.exit(app.exec())

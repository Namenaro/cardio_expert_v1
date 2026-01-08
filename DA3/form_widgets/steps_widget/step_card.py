from DA3 import app_signals
from DA3.app_signals import ParamsInitTrackEditor
from DA3.form_widgets.steps_widget.track_card import TrackCard
from DA3.form_widgets.steps_widget.step_info_card import StepInfoCard
from CORE.db_dataclasses import *

from typing import List
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QFrame, QApplication
)
from PySide6.QtCore import Qt, Slot


class StepCard(QWidget):
    def __init__(self, step: Step, parent=None):
        super().__init__(parent)
        self.step:Step = step
        self.track_cards = []
        self.setup_ui()

    def setup_ui(self):
        # Основной горизонтальный макет (левая и правая части)
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Левая часть — StepInfoCard
        self.step_info_card = StepInfoCard(self.step)
        main_layout.addWidget(self.step_info_card, 1)  # Коэффициент растяжения 1

        # Правая часть — колонка с TrackCard и кнопка
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 2)  # Коэффициент растяжения 2

        # Область прокрутки для TrackCard (если треков много)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QFrame()
        self.tracks_layout = QVBoxLayout(scroll_content)
        self.tracks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(scroll_content)
        right_layout.addWidget(scroll_area)

        # Заполняем TrackCard для каждого трека
        for track in self.step.tracks:
            track_card = TrackCard(track=track, step_id=self.step.id)
            self.track_cards.append(track_card)
            self.tracks_layout.addWidget(track_card)

        # Кнопка "добавить новый трек"
        self.add_track_button = QPushButton("Добавить новый трек")
        self.add_track_button.clicked.connect(self.on_add_track_clicked)
        right_layout.addWidget(self.add_track_button, alignment=Qt.AlignmentFlag.AlignBottom)

    @Slot()
    def on_add_track_clicked(self):
        # Обработчика нажатия кнопки добавления нового трека в шаг
        req_track_params = ParamsInitTrackEditor(track=None, step_id=self.step.id)
        app_signals.track.request_track_redactor.emit(req_track_params)



# Mock-тестирование
if __name__ == "__main__":
    import sys
    from dataclasses import field
    from typing import Optional


    # Создаем mock-данные для тестирования
    point1 = Point(name="Целевая точка")
    point2 = Point(name="Левая точка")
    point3 = Point(name="Правая точка")

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

    step = Step(
        num_in_form=1,
        target_point=point1,
        id=1,
        tracks=[track1, track2],
        right_point=point3,
        left_point=point2,
        left_padding_t=0.5,
        right_padding_t=1.2,
        comment="Пример комментария для шага"
    )

    # Инициализируем приложение
    app = QApplication(sys.argv)

    # Создаем и показываем виджет
    widget = StepCard(step)
    widget.setWindowTitle("StepCard Test")
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
from DA3 import app_signals
from DA3.app_signals import ParamsInitTrackEditor
from DA3.main_app_widgets.form_widgets.steps_widget.track_card import TrackCard
from DA3.main_app_widgets.form_widgets.steps_widget.step_info_card import StepInfoCard
from CORE.db_dataclasses import *

from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Slot
from DA3.base_widget import BaseWidget


class StepCard(BaseWidget):
    def __init__(self, step: Step, parent=None):
        super().__init__(parent)
        self.step: Step = step
        self.track_cards = []
        self.setup_ui()
        self.apply_styles("step_card.qss")  # Только свой уникальный стиль

    def setup_ui(self):
        # Основной горизонтальный макет
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Левая часть — StepInfoCard
        self.step_info_card = StepInfoCard(self.step)
        main_layout.addWidget(self.step_info_card, 1)

        # Правая часть
        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)
        main_layout.addLayout(right_layout, 2)

        # Область прокрутки для TrackCard
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none;")

        scroll_content = QFrame()
        scroll_content.setObjectName("tracksContainer")
        self.tracks_layout = QVBoxLayout(scroll_content)
        self.tracks_layout.setSpacing(8)
        self.tracks_layout.setContentsMargins(8, 8, 8, 8)
        self.tracks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(scroll_content)
        right_layout.addWidget(scroll_area)

        # Заполняем TrackCard для каждого трека
        for track in self.step.tracks:
            track_card = TrackCard(track=track, step_id=self.step.id)
            self.track_cards.append(track_card)
            self.tracks_layout.addWidget(track_card)

        # Кнопка добавления трека
        self.add_track_button = QPushButton("+ Добавить трек")
        self.add_track_button.setObjectName("addTrackButton")
        self.add_track_button.clicked.connect(self.on_add_track_clicked)
        right_layout.addWidget(self.add_track_button)

    @Slot()
    def on_add_track_clicked(self):
        req_track_params = ParamsInitTrackEditor(track=None, step_id=self.step.id)
        app_signals.track.request_track_redactor.emit(req_track_params)
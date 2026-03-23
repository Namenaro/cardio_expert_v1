from CORE.db_dataclasses import *
from typing import List
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QFormLayout, QLabel, QApplication, QMenu
)
from PySide6.QtCore import Qt, QEvent, Slot
from PySide6.QtGui import QMouseEvent

from DA3 import app_signals
from DA3.app_signals import ParamsInitTrackEditor


class TrackCard(QFrame):
    # Начальный стиль виджета
    _DEFAULT_STYLE = """
        TrackCard {
            background-color: #fef7e8;
            border: 1px solid #ffd699;
            border-radius: 8px;
            margin: 4px 0;
        }
    """

    def __init__(self, track: Track, step_id: int, parent=None):
        super().__init__(parent)

        self.track = track
        self.step_id = step_id

        self.setMouseTracking(True)
        self._is_hovered = False

        # Устанавливаем начальный стиль
        self.setStyleSheet(self._DEFAULT_STYLE)

        self.setup_ui()

    def setup_ui(self):
        # Основной макет
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(layout)

        # Форма для отображения данных
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        layout.addLayout(form_layout)

        # ID
        self.id_label = QLabel()
        if self.track.id is not None:
            self.id_label.setNum(self.track.id)
        self.id_label.setObjectName("idLabel")  # Добавляем метку для CSS
        form_layout.addRow("ID:", self.id_label)

        # Длина списка SMs
        self.sms_count_label = QLabel()
        self.sms_count_label.setNum(len(self.track.SMs))
        form_layout.addRow("Количество SM:", self.sms_count_label)

        # Длина списка PSs
        self.pss_count_label = QLabel()
        self.pss_count_label.setNum(len(self.track.PSs))
        form_layout.addRow("Количество PS:", self.pss_count_label)

    @Slot(QEvent)
    def enterEvent(self, event: QEvent):
        self._is_hovered = True
        self._update_style()
        super().enterEvent(event)

    @Slot(QEvent)
    def leaveEvent(self, event: QEvent):
        self._is_hovered = False
        self._update_style()
        super().leaveEvent(event)

    @Slot(QMouseEvent)
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_track_editor()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def open_track_editor(self):
        req_track_params = ParamsInitTrackEditor(track=self.track, step_id=self.step_id)
        app_signals.track.request_track_redactor.emit(req_track_params)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        delete_action = menu.addAction("Удалить трек")
        delete_action.triggered.connect(self.delete_track)
        menu.exec(pos)

    def delete_track(self):
        app_signals.track.db_delete_track.emit(self.track)

    def _update_style(self):
        if self._is_hovered:
            self.setStyleSheet("""
                TrackCard {
                    background-color: #fff5e6;
                    border: 1px solid #ffb347;
                    border-radius: 8px;
                    margin: 4px 0;
                }
            """)
        else:
            self.setStyleSheet(self._DEFAULT_STYLE)


# Mock-тестирование
if __name__ == "__main__":
    import sys

    # Создаем mock-данные для тестирования
    pazzle1 = BasePazzle()
    pazzle2 = BasePazzle()
    pazzle3 = BasePazzle()
    pazzle4 = BasePazzle()

    track = Track(
        id=201,
        SMs=[pazzle1, pazzle2, pazzle3],
        PSs=[pazzle4]
    )

    app = QApplication(sys.argv)

    widget = TrackCard(track, step_id=0)
    widget.setWindowTitle("TrackCard Test")
    widget.resize(300, 200)
    widget.show()

    sys.exit(app.exec())
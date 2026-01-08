from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                               QVBoxLayout, QWidget, QFrame, QLabel, QSizePolicy, QDialog, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from typing import List, Optional
from dataclasses import field
import logging

from CORE.db_dataclasses import Track, BasePazzle, BaseClass
from DA3 import app_signals
from DA3.app_signals import AddSMParams, AddPSParams
from DA3.redactors_widgets.track_redactor.SM_PS_card import SM_PS_Card


class TrackRedactor(QDialog):
    def __init__(self, track: Optional[Track],
                 step_id: int,
                 PSs_refs: List[BaseClass],
                 SMs_refs: List[BaseClass],
                 parent=None):
        """
        Модальный редактор одного трека.
        Позволяет запускать операции добавления/удаления/редактирования пазлов в треке.

        :param track: Если None, то будет создаваться с нуля новый трек
        :param step_id: номер шага, к которому этот трек принадлежит в форме
        :param PSs_refs: библиотека PS-классов
        :param SMs_refs: библиотека SM-классов
        :param parent: окно-родитель для этого QDialog-а
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        self.track = track
        self.step_id = step_id
        self.PSs_refs = PSs_refs
        self.SMs_refs = SMs_refs

        self.setup_ui()

    def setup_ui(self):
        """Инициализация пользовательского интерфейса редактора трека."""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(230, 240, 240))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        self.setLayout(self.main_layout)
        self.setMinimumSize(300, 200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.refresh_ui()

    def refresh_ui(self):
        """Основной метод построения/обновления интерфейса."""
        self._clear_layout(self.main_layout)

        # Добавляем заголовок
        self._add_header()

        # Добавляем основной контент
        if self.track is None:
            self._add_creation_buttons()
        else:
            self._add_puzzle_cards()

        # Принудительное обновление
        self.updateGeometry()
        self.adjustSize()

        if not self.isVisible():
            self.show()

    def _add_header(self):
        """Добавляет заголовок с ID трека."""
        track_id = 'N/A' if self.track is None else self.track.id
        self.id_label = QLabel(f"Track ID: {track_id or 'N/A'}")
        self.id_label.setAlignment(Qt.AlignCenter)
        self.id_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #444;")
        self.main_layout.addWidget(self.id_label)

    def _add_creation_buttons(self):
        """Добавляет кнопки для создания нового трека."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.add_sm_button = QPushButton("Добавить SM")
        self.add_sm_button.clicked.connect(self.on_add_sm)
        buttons_layout.addWidget(self.add_sm_button)

        self.add_ps_button = QPushButton("Добавить PS")
        self.add_ps_button.clicked.connect(self.on_add_ps)
        buttons_layout.addWidget(self.add_ps_button)

        self.main_layout.addLayout(buttons_layout)

    def _add_puzzle_cards(self):
        """Добавляет карточки существующих пазлов."""
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        # Добавляем карточки SM
        for idx, puzzle in enumerate(self.track.SMs or []):
            card = SM_PS_Card(
                puzzle=puzzle,
                refs=self.SMs_refs,
                track_id=self.track.id,
                step_id=self.step_id,
                num_in_track=idx
            )
            cards_layout.addWidget(card)

        # Добавляем карточки PS
        for puzzle in self.track.PSs or []:
            card = SM_PS_Card(
                puzzle=puzzle,
                refs=self.PSs_refs,
                track_id=self.track.id,
                step_id=self.step_id,
                num_in_track=-1
            )
            cards_layout.addWidget(card)

        self.main_layout.addLayout(cards_layout)

    def refresh(self, track: Track):
        """Обновляет данные трека и перестраивает интерфейс."""
        if track is None:
            raise ValueError("track cannot be None")

        self.track = track
        self.logger.info(f"TrackRedactor.refresh() для трека {self.track.id}")

        self.setUpdatesEnabled(False)
        self.refresh_ui()
        self.setUpdatesEnabled(True)

        QApplication.processEvents()
        self.logger.info("Refresh completed")

    def _clear_layout(self, layout):
        """Рекурсивно очищает layout."""
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def on_add_sm(self):
        """Обработчик кнопки 'Добавить SM'."""
        self.logger.info(f"Нажата кнопка 'Добавить SM'-> новый трек в шаг {self.step_id}")
        app_sm_params = AddSMParams(sm=None, num_in_track=0, step_id=self.step_id, track_id=None)
        app_signals.base_pazzle.request_sm_redactor.emit(app_sm_params)

    def on_add_ps(self):
        """Обработчик кнопки 'Добавить PS'."""
        self.logger.info(f"Нажата кнопка 'Добавить PS'-> новый трек в шаг {self.step_id}")
        add_ps_params = AddPSParams(ps=None, track_id=None, step_id=self.step_id)
        app_signals.base_pazzle.request_ps_redactor.emit(add_ps_params)

    def closeEvent(self, event):
        """Обрабатывает событие закрытия окна."""
        app_signals.track.track_redactor_closed.emit()
        super().closeEvent(event)


# Мок-тест (без изменений)
if __name__ == "__main__":
    import sys


    class BasePazzle:
        def __init__(self, is_ps: bool = False, comment: str = "Пример комментария"):
            self.id = 1
            self.comment = comment
            self.class_ref: Optional[BaseClass] = None
            self.is_ps = is_ps

        def is_PS(self):
            return self.is_ps

        def is_SM(self):
            return not self.is_ps


    class BaseClass:
        def __init__(self, name: str):
            self.name = name


    sm1 = BasePazzle(is_ps=False, comment="SM комментарий 1")
    sm2 = BasePazzle(is_ps=False, comment="SM комментарий 2")
    ps1 = BasePazzle(is_ps=True, comment="PS комментарий 1")
    ps2 = BasePazzle(is_ps=True, comment="PS комментарий 2")

    sm_refs = [BaseClass("SMClassA"), BaseClass("SMClassB")]
    ps_refs = [BaseClass("PSClassX"), BaseClass("PSClassY")]

    track = Track(
        id=1001,
        SMs=[sm1, sm2],
        PSs=[ps1, ps2]
    )

    step_id = 202

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Тест TrackCard")
    window.resize(800, 400)

    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    main_layout = QVBoxLayout(central_widget)
    main_layout.setAlignment(Qt.AlignTop)
    main_layout.setSpacing(15)

    track_card = TrackRedactor(track, step_id, ps_refs, sm_refs)
    main_layout.addWidget(track_card)

    window.show()
    sys.exit(app.exec())
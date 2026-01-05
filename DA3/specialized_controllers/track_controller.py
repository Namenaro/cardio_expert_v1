"""
Контроллер для управления шагами
"""
from PySide6.QtCore import Slot
from typing import Optional

from DA3.redactors_widgets.track_redactor import TrackRedactor
from CORE.db_dataclasses import Track
from .base_controller import BaseController

from DA3.app_signals import AppSignals, ParamsInitTrackEditor, TrackDbResult


class TrackController(BaseController):
    """Контроллер для операций с треками"""

    def __init__(self, parent):
        super().__init__(parent)
        self._track_redactor: Optional[TrackRedactor] = None


    def init_signals(self, track_signals: AppSignals._Track):
        """
        Инициализация сигналов для работы с треками

        Args:
            track_signals: объект с сигналами треков
        """
        # Специфичные сигналы
        track_signals.request_track_redactor.connect(self._open_track_redactor)
        track_signals.track_redactor_closed.connect(self._track_redactor_closed)
        track_signals.need_handle_db_track_result.connect(self._handle_db_track_result)

        # Общие сигналы - связываем с методами базового класса
        track_signals.db_delete_track.connect(self._handle_delete_object)

    @Slot(ParamsInitTrackEditor)
    def _open_track_redactor(self, req_track_params: ParamsInitTrackEditor) -> None:
        # создаем редактор трека и запоминаем ссылку на него!
        model = self.get_model()
        current_form = self.get_current_form()

        if model and current_form:
            PSs_refs = model.get_PSs_classes()
            SMs_refs = model.get_SMs_classes()
            self._track_redactor = TrackRedactor(self.get_main_window(),
                                                 track=req_track_params.track,
                                                 step_id=req_track_params.step_id,
                                                 PSs =PSs_refs,
                                                 SMs = SMs_refs)
            self._track_redactor.exec()

    @Slot()
    def _track_redactor_closed(self):
        self._track_redactor = None

    @Slot(Track)
    def _handle_db_track_result(self, track_db_result:TrackDbResult):
        # Обновление модального окна редактора трека
        if track_db_result.success:
            if self._track_redactor is not None:
                self._track_redactor.refresh(track_db_result.track)
        # Обновление формы или показ ошибки база данных
        self.handle_db_result(success=track_db_result.success, message=track_db_result.message)






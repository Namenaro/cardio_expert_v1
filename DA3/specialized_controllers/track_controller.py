"""
Контроллер для управления шагами
"""
from PySide6.QtCore import Slot
from typing import Optional

from DA3.redactors_widgets.track_redactor import TrackRedactor
from CORE.db_dataclasses import Track
from .base_controller import BaseController

from DA3.app_signals import AppSignals, ParamsInitTrackEditor, AddSMParams, AddPSParams
from ..model import TrackDbResult
from ..redactors_widgets.pazzles_modal_editors import SMEditor


class TrackController(BaseController):
    """Контроллер для операций с треками"""

    def __init__(self, parent):
        super().__init__(parent)
        self._track_redactor: Optional[TrackRedactor] = None


    def init_signals(self, track_signals: AppSignals._Track, pazzle_signals: AppSignals._BasePazzle):
        """
        Инициализация сигналов для работы с треками

        Args:
            track_signals: объект с сигналами треков
        """
        # Специфичные сигналы
        track_signals.request_track_redactor.connect(self._open_track_redactor)
        track_signals.track_redactor_closed.connect(self._track_redactor_closed)

        pazzle_signals.db_add_sm.connect(self._add_sm)
        pazzle_signals.db_add_pc.connect(self._add_ps)

        pazzle_signals.request_sm_redactor.connect(self._open_sm_redactor)
        pazzle_signals.request_ps_redactor.connect(self._open_ps_redactor)

        # Общие сигналы - связываем с методами базового класса
        track_signals.db_delete_track.connect(self._handle_delete_object)

    def _open_sm_redactor(self, add_sm_params: AddSMParams)-> None:
        self.logger.info("Открываем редактор SM объекта")
        model = self.get_model()
        sm_refs =model.get_SMs_classes()
        track = None if add_sm_params.track_id is None else model.get_track_by_id(add_sm_params.track_id)
        editor = SMEditor(sm=add_sm_params.sm,
                          step_id=add_sm_params.step_id,
                          classes_refs=sm_refs,
                          track=track,
                          num_in_track=add_sm_params.num_in_track,
                          parent=self.get_main_window())
        editor.exec()

    def _open_ps_redactor(self, add_ps_params: AddPSParams)-> None:
        self.logger.info("Открываем редактор PS объекта")
        #TODO

    @Slot(AddSMParams)
    def _add_sm(self, add_sm_params: AddSMParams)-> None:
        model = self.get_model()
        add_result = model.add_SM(num_in_track=add_sm_params.num_in_track,
                     track_id=add_sm_params.track_id,
                     step_id=add_sm_params.step_id,
                     obj=add_sm_params.sm
                     )
        self._handle_db_track_result(add_result)

    @Slot(AddPSParams)
    def _add_ps(self, add_ps_params: AddPSParams)-> None:
        model = self.get_model()
        add_result = model.add_PS(track_id=add_ps_params.track_id,
                     step_id=add_ps_params.step_id,
                     obj=add_ps_params.sm)
        self._handle_db_track_result(add_result)

    @Slot(ParamsInitTrackEditor)
    def _open_track_redactor(self, req_track_params: ParamsInitTrackEditor) -> None:
        # создаем редактор трека и запоминаем ссылку на него!
        model = self.get_model()
        current_form = self.get_current_form()

        if model and current_form:
            PSs_refs = model.get_PSs_classes()
            SMs_refs = model.get_SMs_classes()
            self._track_redactor = TrackRedactor(parent=self.get_main_window(),
                                                 track=req_track_params.track,
                                                 step_id=req_track_params.step_id,
                                                 PSs_refs =PSs_refs,
                                                 SMs_refs = SMs_refs)
            self._track_redactor.exec()

    @Slot()
    def _track_redactor_closed(self):
        self._track_redactor = None


    def _handle_db_track_result(self, track_db_result:TrackDbResult):
        # Обновление модального окна редактора трека
        if track_db_result.success:
            if self._track_redactor is not None:
                self._track_redactor.refresh(track_db_result.track)
        # Обновление формы или показ ошибки база данных
        self.handle_db_result(success=track_db_result.success, message=track_db_result.message)






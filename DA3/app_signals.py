from PySide6.QtCore import QObject, Signal
from typing import Optional, Union, NamedTuple
from CORE.db_dataclasses import *


# Вспомогательные типы для явной документации аргументов сигналов
class AddSMParams(NamedTuple):
    sm: BasePazzle
    track_id: int
    num_in_track: int

class AddPSParams(NamedTuple):
    ps: BasePazzle
    track_id: int
    num_in_track: int

class AddTrackParams(NamedTuple):
    track: Track
    step_id: int


class _SignalCategory(QObject):
    """Базовый класс для категорий сигналов."""
    pass


class AppSignals:
    """
    Глобальные сигналы приложения, сгруппированные по функциональным областям.
    """

    class _Form(_SignalCategory):
        request_main_info_redactor = Signal(Form)
        db_add_form = Signal(Form)
        db_update_form_main_info = Signal(Form)

    class _Point(_SignalCategory):
        request_point_redactor = Signal(Point)
        db_add_point = Signal(Point)

    class _Parameter(_SignalCategory):
        request_parameter_redactor = Signal(Parameter)
        db_add_parameter = Signal(Parameter)

    class _Track(_SignalCategory):
        request_track_redactor = Signal(Track)
        db_add_track = Signal(AddTrackParams)

    class _Step(_SignalCategory):
        request_new_step_dialog = Signal()
        request_step_info_redactor = Signal(Step)
        db_add_step = Signal(Step)

    class _BasePazzle(_SignalCategory):
        # Запросы на показ модальных редакторов
        request_hc_redactor = Signal(BasePazzle)
        request_pc_redactor = Signal(BasePazzle)
        request_sm_redactor = Signal(BasePazzle)
        request_ps_redactor = Signal(BasePazzle)

        # Запрос на добавление в базу нового пазла
        db_add_hc = Signal(BasePazzle)
        db_add_pc = Signal(BasePazzle)
        db_add_sm = Signal(AddSMParams)
        db_add_ps = Signal(AddPSParams)

    class _DBActions(_SignalCategory):
        db_delete_object = Signal(object)
        db_update_object = Signal(object)

    # Экземпляры категорий
    form = _Form()
    point = _Point()
    parameter = _Parameter()
    track = _Track()
    step = _Step()
    base_pazzle = _BasePazzle()
    db_actions = _DBActions()
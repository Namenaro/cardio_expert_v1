from PySide6.QtCore import QObject, Signal

from typing import List, Optional, Union

from CORE.db_dataclasses import *


class AppSignals(QObject):
    """
    Глобальные сигналы приложения
    """

    # ===================== СИГНАЛЫ ОТКРЫТИЯ РЕДАКТОРОВ =====================

    request_main_info_redactor = Signal(Form, object)
    request_point_redactor = Signal(Optional[Point], object)
    request_parameter_redactor = Signal(Optional[Parameter], object)
    request_step_redactor = Signal(Optional[Step], object)

    request_hc_redactor = Signal(Optional[BasePazzle], object)
    request_pc_redactor = Signal(Optional[BasePazzle], object)
    request_sm_redactor = Signal(Optional[BasePazzle], object)
    request_ps_redactor = Signal(Optional[BasePazzle], object)

    # ===================== СИГНАЛЫ ДЕЙСТВИЙ С БАЗОЙ =====================
    # СИГНАЛЫ ОБНОВЛЕНИЯ И УДАЛЕНИЯ
    DatabaseObject = Union[Form, Point, Parameter, Step, BasePazzle, Track]
    db_delete_object = Signal(DatabaseObject)
    db_update_object = Signal(DatabaseObject)

    # СИГНАЛЫ ДОБАВЛЕНИЯ
    db_add_form = Signal(Form)
    db_add_point = Signal(Point)
    db_add_parameter = Signal(Parameter)
    db_add_step = Signal(Step)
    db_add_track = Signal(Track, int) # track, step_id

    db_add_hc = Signal(BasePazzle)
    db_add_pc = Signal(BasePazzle)
    db_add_sm = Signal(BasePazzle, int, int) # sm, track_id, num_in_track
    db_add_ps = Signal(BasePazzle, int, int) # ps, track_id, num_in_track







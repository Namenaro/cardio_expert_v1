from PySide6.QtCore import QObject, Signal

from typing import List, Optional, Union

from CORE.db_dataclasses import *


class AppSignals(QObject):
    """
    Глобальные сигналы приложения
    """

    # ===================== СИГНАЛЫ ОТКРЫТИЯ РЕДАКТОРОВ =====================

    request_main_info_redactor = Signal(Form)
    request_point_redactor = Signal(Point)
    request_parameter_redactor = Signal(Parameter)
    request_track_redactor = Signal(Track)

    request_hc_redactor = Signal(BasePazzle)
    request_pc_redactor = Signal(BasePazzle)
    request_sm_redactor = Signal(BasePazzle)
    request_ps_redactor = Signal(BasePazzle)

    request_new_step_dialog = Signal()
    request_step_info_redactor = Signal(Step)

    # ===================== СИГНАЛЫ ДЕЙСТВИЙ С БАЗОЙ =====================
    # СИГНАЛЫ ОБНОВЛЕНИЯ И УДАЛЕНИЯ

    db_delete_object = Signal(object) # Form, Point, Parameter, Step, BasePazzle, Track
    db_update_object = Signal(object) # Form, Point, Parameter, Step, BasePazzle, Track
    db_update_form_main_info = Signal(Form)

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

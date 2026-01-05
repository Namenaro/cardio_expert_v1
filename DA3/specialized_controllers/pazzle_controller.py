"""
Контроллер для управления головоломками (HC/PC)
"""
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

from DA3.redactors_widgets import HCEditor, PCEditor
from CORE.db_dataclasses import BasePazzle
from .base_controller import BaseController

if TYPE_CHECKING:
    from DA3.app_signals import AppSignals


class PazzleController(BaseController):
    """Контроллер для операций с головоломками (HC/PC)"""

    def __init__(self, parent):
        super().__init__(parent)

    def init_signals(self, base_pazzle_signals: 'AppSignals._BasePazzle'):
        """
        Инициализация сигналов для работы с головоломками

        Args:
            base_pazzle_signals: объект с сигналами головоломок (app_signals._BasePazzle)
        """
        # Специфичные сигналы редакторов
        base_pazzle_signals.request_hc_redactor.connect(self._open_hc_redactor)
        base_pazzle_signals.request_pc_redactor.connect(self._open_pc_redactor)
        base_pazzle_signals.request_sm_redactor.connect(self._open_sm_redactor)
        base_pazzle_signals.request_ps_redactor.connect(self._open_ps_redactor)

        # Специфичные сигналы добавления
        base_pazzle_signals.db_add_hc.connect(self._handle_add_hc)
        base_pazzle_signals.db_add_pc.connect(self._handle_add_pc)
        base_pazzle_signals.db_add_sm.connect(self._handle_add_sm)
        base_pazzle_signals.db_add_ps.connect(self._handle_add_ps)

        # Общие сигналы - связываем с методами базового класса
        base_pazzle_signals.db_update_pazzle.connect(self._handle_update_object)
        base_pazzle_signals.db_delete_pazzle.connect(self._handle_delete_object)

    @Slot(BasePazzle)
    def _open_hc_redactor(self, hc: BasePazzle):
        model = self.get_model()
        current_form = self.get_current_form()

        if model and current_form:
            classes_refs = model.get_HCs_classes()
            editor = HCEditor(self.get_main_window(), form=current_form, hc=hc, classes_refs=classes_refs)
            editor.exec()

    @Slot(BasePazzle)
    def _open_pc_redactor(self, pc: BasePazzle):
        model = self.get_model()
        current_form = self.get_current_form()

        if model and current_form:
            classes_refs = model.get_PCs_classes()
            editor = PCEditor(self.get_main_window(), form=current_form, pc=pc, classes_refs=classes_refs)
            editor.exec()

    @Slot(BasePazzle)
    def _open_sm_redactor(self, sm: BasePazzle):
        # TODO: Реализовать редактор SM
        self.logger.warning("Редактор SM еще не реализован")

    @Slot(BasePazzle)
    def _open_ps_redactor(self, ps: BasePazzle):
        # TODO: Реализовать редактор PS
        self.logger.warning("Редактор PS еще не реализован")

    @Slot(BasePazzle)
    def _handle_add_hc(self, hc: BasePazzle):
        """Обработчик добавления объекта типа HC"""
        current_form = self.get_current_form()
        model = self.get_model()

        if model and current_form:
            success, message = model.add_HC(hc, form_id=current_form.id)
            self.handle_db_result(success, message)

    @Slot(BasePazzle)
    def _handle_add_pc(self, pc: BasePazzle):
        """Обработчик добавления объекта типа PC"""
        current_form = self.get_current_form()
        model = self.get_model()

        if model and current_form:
            success, message = model.add_PC(pc, form_id=current_form.id)
            self.handle_db_result(success, message)

    @Slot(object)
    def _handle_add_sm(self, add_params):
        """Обработчик добавления объекта типа SM"""
        # TODO: Реализовать добавление SM
        self.logger.warning("Добавление SM еще не реализован")

    @Slot(object)
    def _handle_add_ps(self, add_params):
        """Обработчик добавления объекта типа PS"""
        # TODO: Реализовать добавление PS
        self.logger.warning("Добавление PS еще не реализован")
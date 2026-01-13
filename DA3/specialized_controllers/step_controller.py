"""
Контроллер для управления шагами
"""
from PySide6.QtCore import Slot


from DA3.redactors_widgets import StepInfoEditor
from DA3.form_widgets.dialog_new_step import AddStepDialog
from CORE.db_dataclasses import Step
from .base_controller import BaseController

from DA3.app_signals import AppSignals


class StepController(BaseController):
    """Контроллер для операций с шагами"""

    def __init__(self, parent):
        super().__init__(parent)

    def init_signals(self, step_signals: AppSignals._Step):
        """
        Инициализация сигналов для работы с шагами

        Args:
            step_signals: объект с сигналами шагов (app_signals._Step)
        """
        # Специфичные сигналы шагов
        step_signals.request_new_step_dialog.connect(self._open_step_add_dialog)
        step_signals.request_step_info_redactor.connect(self._open_step_info_redactor)
        step_signals.db_add_step.connect(self._handle_add_step)

        # Общие сигналы - связываем с методами базового класса
        step_signals.db_update_step.connect(self._handle_update_object)
        step_signals.db_delete_step.connect(self._handle_delete_object)

    @Slot()
    def _open_step_add_dialog(self) -> None:
        current_form = self.get_current_form()
        if current_form:
            dialog = AddStepDialog(parent=self.get_main_window(), points=current_form.points)
            dialog.exec()

    @Slot(Step)
    def _open_step_info_redactor(self, step: Step) -> None:
        current_form = self.get_current_form()
        if current_form:
            editor = StepInfoEditor(
                parent=self.get_main_window(),
                points=current_form.points,
                step=step
            )
            editor.exec()

    @Slot(Step)
    def _handle_add_step(self, step: Step) -> None:
        """Обработчик добавления шага"""
        current_form = self.get_current_form()
        model = self.get_model()

        if current_form is None or current_form.id is None:
            self.show_error("Нет текущей формы для добавления шага")
            return

        if model:
            success, message = model.add_step(step, current_form.id)
            self.handle_db_result(success, message)
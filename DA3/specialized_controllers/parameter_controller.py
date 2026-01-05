"""
Контроллер для управления параметрами
"""
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

from DA3.redactors_widgets import ParameterEditor
from CORE.db_dataclasses import Parameter
from DA3.specialized_controllers.base_controller import BaseController

if TYPE_CHECKING:
    from DA3.app_signals import AppSignals


class ParameterController(BaseController):
    """Контроллер для операций с параметрами"""

    def __init__(self, parent):
        super().__init__(parent)

    def init_signals(self, parameter_signals: 'AppSignals._Parameter'):
        """
        Инициализация сигналов для работы с параметрами

        Args:
            parameter_signals: объект с сигналами параметров (app_signals._Parameter)
        """
        # Специфичные для параметров сигналы
        parameter_signals.request_parameter_redactor.connect(self._open_parameter_redactor)
        parameter_signals.db_add_parameter.connect(self._handle_add_parameter)

        # Общие сигналы - связываем с методами базового класса
        parameter_signals.db_update_parameter.connect(self._handle_update_object)
        parameter_signals.db_delete_parameter.connect(self._handle_delete_object)

    @Slot(Parameter)
    def _open_parameter_redactor(self, parameter: Parameter) -> None:
        editor = ParameterEditor(self.get_main_window(), parameter)
        editor.exec()

    @Slot(Parameter)
    def _handle_add_parameter(self, parameter: Parameter) -> None:
        """Обработчик добавления параметра"""
        current_form = self.get_current_form()
        model = self.get_model()

        if current_form is None or current_form.id is None:
            self.show_error("Нет текущей формы для добавления параметра")
            return

        if model:
            success, message = model.add_parameter(parameter, current_form.id)
            self.handle_db_result(success, message)
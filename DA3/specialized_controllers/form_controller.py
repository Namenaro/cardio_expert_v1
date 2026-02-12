"""
Контроллер для управления формами
"""
from PySide6.QtCore import Slot

from DA3.redactors_widgets import FormEditor
from CORE.db_dataclasses import Form
from DA3.specialized_controllers.base_controller import BaseController
from DA3.app_signals import AppSignals


class FormController(BaseController):
    """Контроллер для операций с формами"""

    def __init__(self, parent):
        super().__init__(parent)

    def init_signals(self, form_signals: AppSignals._Form):
        """
        Инициализация сигналов для работы с формами

        Args:
            form_signals: объект с сигналами формы (app_signals._Form)
        """
        form_signals.request_main_info_redactor.connect(self._open_main_info_redactor)
        form_signals.db_add_form.connect(self._handle_add_form)
        form_signals.db_update_form_main_info.connect(self._handle_update_form_main_info)
        form_signals.db_delete_form.connect(self._handle_delete_form)

    @Slot(Form)
    def _open_main_info_redactor(self, form: Form) -> None:
        """
        Открытие редактора основной информации формы

        Args:
            form: объект Form для редактирования
        """
        editor = FormEditor(self.get_main_window(), form)
        editor.exec()

    @Slot(Form)
    def _handle_add_form(self, form: Form) -> None:
        """Обработчик добавления новой формы"""
        model = self.get_model()
        if model:
            success, message = model.add_form(form)
            if success:
                self.set_current_form(form)
            self.handle_db_result(success, message)

    @Slot(Form)
    def _handle_update_form_main_info(self, form: Form) -> None:
        """Обработчик обновления основной информации формы"""
        model = self.get_model()
        if model:
            success, message = model.update_main_info(form)
            self.handle_db_result(success, message)

    @Slot(Form)
    def _handle_delete_form(self, form: Form) -> None:
        """Обработчик удаления формы"""
        model = self.get_model()
        if model:
            success, message = model.delete_object(form)
            if success:
                self.show_success(message)
                self.reinit_by_empty()
            else:
                self.show_error(message)

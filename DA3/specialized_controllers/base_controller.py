"""
Базовый класс для всех специализированных контроллеров
"""

import logging
from typing import Optional
from PySide6.QtCore import QObject, Slot

from CORE.db_dataclasses import Form

from DA3.model import Model

class BaseController(QObject):
    """Базовый контроллер с общими методами"""

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.parent_controller = parent  # Ссылка на главный контроллер

    def init_signals(self, signals):
        """
        Инициализация сигналов контроллера

        Args:
            signals: конкретный класс сигналов для данного контроллера
        """
        raise NotImplementedError("Метод init_signals должен быть реализован в дочернем классе")

    def get_model(self)->Model:
        """Получить модель из родительского контроллера"""
        return self.parent_controller.model if hasattr(self.parent_controller, 'model') else None

    def get_main_window(self):
        """Получить главное окно из родительского контроллера"""
        return self.parent_controller.main_window if hasattr(self.parent_controller, 'main_window') else None

    def get_current_form(self) -> Optional[Form]:
        """Получить текущую форму из родительского контроллера"""
        return self.parent_controller.current_form if hasattr(self.parent_controller, 'current_form') else None

    def set_current_form(self, form: Form) -> None:
        """Установить текущую форму в родительском контроллере"""
        if hasattr(self.parent_controller, 'current_form'):
            self.parent_controller.current_form = form

    def refresh_form_data(self) -> None:
        """Обновить данные формы через родительский контроллер"""
        if hasattr(self.parent_controller, 'refresh_form_data') and self.get_current_form():
            self.parent_controller.refresh_form_data(self.get_current_form().id)

    def show_success(self, message: str) -> None:
        """Показать сообщение об успехе через родительский контроллер"""
        if hasattr(self.parent_controller, '_show_success'):
            self.parent_controller._show_success(message)

    def show_error(self, message: str) -> None:
        """Показать сообщение об ошибке через родительский контроллер"""
        if hasattr(self.parent_controller, '_show_error'):
            self.parent_controller._show_error(message)

    def handle_db_result(self, success: bool, message: str) -> None:
        """Обработка результата операции с БД"""
        if success:
            self.refresh_form_data()
            self.show_success(message)
        else:
            self.show_error(message)

    def _handle_update_object(self, obj) -> None:
        """Общий обработчик обновления объекта"""
        model = self.get_model()
        if model:
            success, message = model.update_object(obj)
            self.handle_db_result(success, message)

    def _handle_delete_object(self, obj) -> None:
        """Общий обработчик удаления объекта"""
        model = self.get_model()
        if model:
            success, message = model.delete_object(obj)
            self.handle_db_result(success, message)
"""
Контроллер для управления точками
"""
from PySide6.QtCore import Slot
from typing import TYPE_CHECKING

from DA3.redactors_widgets import PointEditor
from CORE.db_dataclasses import Point
from DA3.specialized_controllers.base_controller import BaseController

if TYPE_CHECKING:
    from DA3.app_signals import AppSignals


class PointController(BaseController):
    """Контроллер для операций с точками"""

    def __init__(self, parent):
        super().__init__(parent)

    def init_signals(self, point_signals: 'AppSignals._Point'):
        """
        Инициализация сигналов для работы с точками

        Args:
            point_signals: объект с сигналами точек (app_signals._Point)
        """
        # Специфичные для точек сигналы
        point_signals.request_point_redactor.connect(self._open_point_redactor)
        point_signals.db_add_point.connect(self._handle_add_point)

        # Общие сигналы - связываем с методами базового класса
        point_signals.db_opdate_point.connect(self._handle_update_object)
        point_signals.db_delete_point.connect(self._handle_delete_object)

    @Slot(Point)
    def _open_point_redactor(self, point: Point) -> None:
        """
        Открытие редактора точки

        Args:
            point: объект Point для редактирования
        """
        editor = PointEditor(self.get_main_window(), point)
        editor.exec()

    @Slot(Point)
    def _handle_add_point(self, point: Point) -> None:
        """Обработчик добавления точки"""
        current_form = self.get_current_form()
        model = self.get_model()

        if current_form is None or current_form.id is None:
            self.show_error("Нет текущей формы для добавления точки")
            return

        if model:
            success, message = model.add_point(point, current_form.id)
            self.handle_db_result(success, message)
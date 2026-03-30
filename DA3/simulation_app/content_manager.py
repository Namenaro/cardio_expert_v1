# DA3/simulation_app/content_manager.py

from enum import Enum
from typing import Optional
from PySide6.QtWidgets import QWidget, QStackedWidget

from CORE.run import Exemplar
from CORE.visual_debug import TrackRes
from DA3.simulation_app.simulation_widgets.track_res_widget import TrackResWidget
from DA3.simulation_app.simulation_widgets.exemplar_widget import ExemplarWidget
from DA3.simulation_app.simulation_widgets.empty_widget import EmptyWidget


class ContentType(Enum):
    """Типы контента для правой панели"""
    EMPTY = "empty"
    EXEMPLAR = "exemplar"
    TRACK = "track"


class ContentManager:
    """
    Управляет правой панелью главного окна.
    """

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.stacked_widget = QStackedWidget()

        # Создаем виджеты
        self._create_empty_widget()
        self._create_exemplar_widget()
        self._create_track_widget()

    def _create_empty_widget(self) -> None:
        """Создает пустой виджет"""
        self.empty_widget = EmptyWidget()
        self.stacked_widget.addWidget(self.empty_widget)

    def _create_exemplar_widget(self) -> None:
        """Создает виджет для экземпляра датасета"""
        self.exemplar_widget = ExemplarWidget()
        self.stacked_widget.addWidget(self.exemplar_widget)

    def _create_track_widget(self) -> None:
        """Создает виджет для Track результата"""
        self.track_widget = TrackResWidget()
        self.stacked_widget.addWidget(self.track_widget)

    def show_exemplar(self, exemplar: Exemplar, color: str = 'green') -> None:
        """Показывает виджет с текущим экземпляром датасета"""
        if hasattr(self.exemplar_widget, 'reset_data'):
            self.exemplar_widget.reset_data(exemplar, color)
        self.stacked_widget.setCurrentWidget(self.exemplar_widget)

    def show_track(self, track_res: TrackRes) -> None:
        """Показывает виджет с результатами трека"""
        if hasattr(self.track_widget, 'reset_data'):
            self.track_widget.reset_data(track_res)
        self.stacked_widget.setCurrentWidget(self.track_widget)

    def show_empty(self, error_message: Optional[str] = None) -> None:
        """Показывает пустой виджет"""
        if error_message and hasattr(self.empty_widget, 'set_error_message'):
            self.empty_widget.set_error_message(error_message)
        elif hasattr(self.empty_widget, 'clear_error'):
            self.empty_widget.clear_error()
        self.stacked_widget.setCurrentWidget(self.empty_widget)

    def get_widget(self) -> QStackedWidget:
        """Возвращает QStackedWidget для встраивания в главную форму"""
        return self.stacked_widget

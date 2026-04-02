# DA3/simulation_app/content_manager.py

from enum import Enum
from typing import Optional

from PySide6.QtWidgets import QWidget, QStackedWidget

from CORE.run import Exemplar
from CORE.visual_debug import TrackRes, StepRes, SM_Res, PS_Res
from DA3.simulation_app.simulation_widgets.empty_widget import EmptyWidget
from DA3.simulation_app.simulation_widgets.exemplar_widget import ExemplarWidget
from DA3.simulation_app.simulation_widgets.step_res_widget import StepResWidget
from DA3.simulation_app.simulation_widgets.track_res_widget import TrackFullResWidget
from DA3.simulation_app.simulation_widgets.SM_res_widget import SM_ResWidget
from DA3.simulation_app.simulation_widgets.PS_res_widget import PS_ResWidget


class ContentType(Enum):
    """Типы контента для правой панели"""
    EMPTY = "empty"
    EXEMPLAR = "exemplar"
    TRACK = "track"
    STEP = "step"
    SM = "sm"
    PS = "ps"


class ContentManager:
    """
    Управляет правой панелью главного окна.
    """

    def __init__(self, parent: QWidget):
        self.parent = parent
        self.stacked_widget = QStackedWidget()

        # Создаем виджеты
        self.empty_widget = EmptyWidget()
        self.exemplar_widget = ExemplarWidget()
        self.track_widget = TrackFullResWidget()
        self.step_widget = StepResWidget()
        self.sm_widget = SM_ResWidget()  # НОВЫЙ ВИДЖЕТ
        self.ps_widget = PS_ResWidget()  # НОВЫЙ ВИДЖЕТ

        self.stacked_widget.addWidget(self.empty_widget)
        self.stacked_widget.addWidget(self.exemplar_widget)
        self.stacked_widget.addWidget(self.track_widget)
        self.stacked_widget.addWidget(self.step_widget)
        self.stacked_widget.addWidget(self.sm_widget)  # ДОБАВЛЯЕМ
        self.stacked_widget.addWidget(self.ps_widget)  # ДОБАВЛЯЕМ

    def show_exemplar(self, exemplar: Exemplar, color: str = 'green') -> None:
        """Показывает виджет с текущим экземпляром датасета"""
        self.exemplar_widget.clear()
        self.exemplar_widget.reset_data(exemplar, color)
        self.stacked_widget.setCurrentWidget(self.exemplar_widget)

    def show_track(self, track_res: TrackRes) -> None:
        """Показывает полный виджет с результатами трека"""
        self.track_widget.clear()
        self.track_widget.reset_data(track_res)
        self.stacked_widget.setCurrentWidget(self.track_widget)

    def show_step(self, step_res: StepRes) -> None:
        """Показывает виджет с результатами шага"""
        self.step_widget.clear()
        self.step_widget.reset_data(step_res)
        self.stacked_widget.setCurrentWidget(self.step_widget)

    def show_sm(self, sm_res: SM_Res) -> None:
        """Показывает виджет с результатами SM-пазла"""
        self.sm_widget.clear()
        self.sm_widget.reset_data(sm_res)
        self.stacked_widget.setCurrentWidget(self.sm_widget)

    def show_ps(self, ps_res: PS_Res, ground_true_point: Optional[float] = None) -> None:
        """Показывает виджет с результатами PS-пазла"""
        self.ps_widget.clear()
        self.ps_widget.reset_data(ps_res, ground_true_point)
        self.stacked_widget.setCurrentWidget(self.ps_widget)

    def show_empty(self, error_message: Optional[str] = None) -> None:
        """Показывает пустой виджет"""
        if error_message:
            self.empty_widget.set_error_message(error_message)
        else:
            self.empty_widget.clear_error()
        self.stacked_widget.setCurrentWidget(self.empty_widget)

    def get_widget(self) -> QStackedWidget:
        """Возвращает QStackedWidget для встраивания в главную форму"""
        return self.stacked_widget

    def cleanup(self):
        """Очищает все ресурсы"""
        self.exemplar_widget.cleanup()
        self.track_widget.cleanup()
        self.step_widget.cleanup()
        self.sm_widget.cleanup()  # ДОБАВЛЯЕМ
        self.ps_widget.cleanup()  # ДОБАВЛЯЕМ
        self.empty_widget.cleanup()
        self.stacked_widget.deleteLater()
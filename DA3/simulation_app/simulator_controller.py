import logging
from typing import Optional

from PySide6.QtCore import QObject

from CORE.db_dataclasses import Form
from DA3 import app_signals
from DA3.simulation_app.main_window import MainFormSimulator
from DA3.simulation_app.simulator import Simulator
from DA3.simulation_app.simulator_signals import get_signals

logger = logging.getLogger(__name__)


class SimulatorController(QObject):
    def __init__(self, form: Optional[Form] = None):
        super().__init__()
        self.main_window: Optional[MainFormSimulator] = None
        self.simulator = Simulator()

        # Получаем глобальные сигналы
        self.signals = get_signals()

        # Подключаем сигналы к обработчикам
        self._connect_signals()

        if form:
            self.simulator.reset_form(form)
        app_signals.form.form_changed.connect(self.on_form_changed)

    def _connect_signals(self):
        """Подключает все сигналы к их обработчикам"""
        self.signals.step_selected.connect(self.on_step_selected)
        self.signals.track_selected.connect(self.on_track_selected)
        self.signals.SM_selected.connect(self.on_sm_selected)
        self.signals.PS_selected.connect(self.on_ps_selected)

    def on_form_changed(self, form: Form):
        self.simulator.reset_form(form)
        if self.main_window:
            self.main_window.update_form(self.get_r_form())

    def on_step_selected(self, step_id: int, num_in_form: int):
        """Обработчик выбора шага"""
        logger.debug(f"Выбран шаг: id={step_id}, num_in_form={num_in_form}")
        # TODO: Добавить логику обработки выбора шага
        pass

    def on_track_selected(self, track_id: int):
        """Обработчик выбора трека"""
        logger.debug(f"Выбран трек: id={track_id}")
        # TODO: Добавить логику обработки выбора трека
        pass

    def on_sm_selected(self, sm_id: int, num_in_track: int):
        """Обработчик выбора SM"""
        print(f"Выбран SM: id={sm_id}, num_in_track={num_in_track}")
        # TODO: Добавить логику обработки выбора SM
        pass

    def on_ps_selected(self, ps_id: int):
        """Обработчик выбора PS"""
        logger.debug(f"Выбран PS: id={ps_id}")
        # TODO: Добавить логику обработки выбора PS
        pass

    def get_r_form(self):
        return self.simulator.rform

    def run(self):
        logger.info("Показываем окно симулятора")
        self.main_window = MainFormSimulator(r_form=self.get_r_form())
        self.main_window.show()
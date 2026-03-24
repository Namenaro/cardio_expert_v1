import logging
from typing import Optional

from PySide6.QtCore import QObject

from CORE.db_dataclasses import Form
from DA3 import app_signals
from DA3.simulation_app.main_window import MainFormSimulator
from DA3.simulation_app.simulator import Simulator

logger = logging.getLogger(__name__)


class SimulatorController(QObject):
    def __init__(self, form: Optional[Form] = None):
        super().__init__()
        self.main_window: Optional[MainFormSimulator] = None
        self.simulator = Simulator()
        if form:
            self.simulator.reset_form(form)
        app_signals.form.form_changed.connect(self.on_form_changed)

    def on_form_changed(self, form: Form):
        self.simulator.reset_form(form)
        if self.main_window:
            self.main_window.update_form(self.get_r_form())

    def get_r_form(self):
        return self.simulator.rform

    def run(self):
        logger.info("Показываем окно симулятора")
        self.main_window = MainFormSimulator(r_form=self.get_r_form())
        self.main_window.show()

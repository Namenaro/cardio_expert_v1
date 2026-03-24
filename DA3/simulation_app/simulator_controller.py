import logging
from typing import Optional

from PySide6.QtCore import QObject

from CORE.db_dataclasses import Form
from DA3 import app_signals
from DA3.simulation_app.simulator import Simulator

logger = logging.getLogger(__name__)


class SimulatorController(QObject):
    def __init__(self, form: Optional[Form] = None):
        super().__init__()
        self.simulator = Simulator()
        if form:
            self.simulator.reset_form(form)
        app_signals.form.form_changed.connect(self.on_form_changed)

    def on_form_changed(self, form: Form):
        self.simulator.reset_form(form)

    def run(self):
        logger.info("Показываем окно симулятора")

from PySide6.QtCore import QObject

from DA3.simulation_app.simulator import Simulator


class Controller(QObject):
    def __init__(self):
        super().__init__()
        self.simulator = Simulator()

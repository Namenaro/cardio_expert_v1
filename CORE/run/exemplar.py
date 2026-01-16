from typing import Any

from CORE import Signal
from CORE.logger import get_logger

logger = get_logger(__name__)

class Exemplar:
    """ Экземпляр формы - конкретная расстановка точек на конкретном одномерном сигнале ЭКГ """

    def __init__(self):
        pass

    def add_point(self, point_name: str, point_coord_t: float, track_id: Any) -> None:
        pass

    def contains_point(self, point_name: str) -> bool:
        pass

    def get_point_coord(self, point_name: str) -> float:
        if not self.contains_point(point_name):
            logger.error(f" Точка {point_name} отсутствует в экземпляре формы")
            raise ValueError
        pass

    def add_parameter(self, param_name: str, param_value: Any) -> None:
        pass

    def contains_parameter(self, param_name: str) -> bool:
        pass

    def get_parameter_value(self, param_name: str) -> float:
        if not self.contains_parameter(param_name):
            logger.error(f" Параметр {param_name} отсутствует в экземпляре формы")
            raise ValueError
        pass

    def get_signal(self) -> Signal:
        return self.signal

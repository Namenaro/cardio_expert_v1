from CORE.pazzles_lib.hc_base import HCBase
from CORE.signal_1d import Signal
from typing import Optional, Any
from dataclasses import dataclass


class HigherThanThreshold(HCBase):
    """ Значение параметра выше заданного порога"""

    def __init__(self, threshold: float = 3):
        """
        :param threshold: пороговое значение
        """
        self.threshold = threshold

    def register_input_parameters(self, param_to_eval: float):
        """
        :param param_to_eval: параметр на проверку
        """
        self.param_to_eval = param_to_eval

    def run(self) -> bool:
        if self.param_to_eval > self.threshold:
            return False

        return True


# Пример использования
if __name__ == "__main__":
    # Создаем паззл
    hc = HigherThanThreshold(threshold=3)
    hc.register_input_parameters(param_to_eval=5.5)
    res = hc.run()

    print(f"res = {res}")

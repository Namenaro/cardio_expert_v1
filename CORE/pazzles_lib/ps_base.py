from abc import ABC, abstractmethod
from typing import Optional, List

from CORE import Signal


class PSBase(ABC):
    """Базовый класс для всех классов типа "селектор точек" """

    @abstractmethod
    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> List[float]:
        """
         Выполнение алгоритма выбора точек на интервале [left_t, right_t]

        :param signal: входной сигнал для анализа
        :param left_t: левая граница разрешенного интервала поиска точек
        :param right_t: правая граница разрешенного интервала поиска точек
        :return: список координат точек, выбранных в качестве ключевых алгоритмом этого пазла
        """
        pass

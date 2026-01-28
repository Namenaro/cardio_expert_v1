from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional, List

from CORE import Signal
from CORE.exeptions import PazzleOutOfSignal


class PSBase(ABC):
    """Базовый класс для всех классов типа "селектор точек" """

    @abstractmethod
    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> List[float]:
        """
         Выполнение алгоритма выбора точек на интервале [left_t, right_t]

        :raise PazzleOutOfSignal, если логика пазла потребовала обращения за пределы предоставленного сигнала

        :param signal: входной сигнал для анализа
        :param left_t: левая граница разрешенного интервала поиска точек
        :param right_t: правая граница разрешенного интервала поиска точек
        :return: список координат точек, выбранных в качестве ключевых алгоритмом этого пазла
        """
        pass

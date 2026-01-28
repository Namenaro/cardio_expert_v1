from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional, List

from CORE import Signal


class SMBase(ABC):
    """Базовый класс для всех классов типа "модификация сигнала" """

    @abstractmethod
    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> Signal:
        """
         Выполнение алгоритма изменения сигнала, с возможностью указания интервала [left_t, right_t];
         В зависимости от алгоритма этот интервал может и не использоваться, если предполагается
          необходимость изменить весь сигнал.
          В данном интервале будут искать особые точки PS-пазлы этого трека.

        :raise RunError, код ошибки ErrorCode.RUN_PAZZLE_OUT_OF_SIGNAL, если логика пазла потребовала обращения за пределы предоставленного сигнала

        :param signal: входной сигнал для анализа
        :param left_t: левая граница разрешенного интервала поиска особый точек шага (не ищутся азлом типа SM)
        :param right_t: правая граница разрешенного интервала поиска точек (не ищутся азлом типа SM)
        :return: модифицированный сигнал той же длины
        """
        pass

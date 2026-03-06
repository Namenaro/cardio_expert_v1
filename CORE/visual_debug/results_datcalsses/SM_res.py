from dataclasses import dataclass

from CORE import Signal


@dataclass
class SM_Res:
    id: int  # id пазла в базе

    old_signal: Signal  # сигнал экземпляра до модификации SM-пазлом
    result_signal: Signal  # после модификации

    left_coord: float  # левая координата, заданная в настройках шага, которому принадлежит этот SM
    right_coord: float  # правая. Вместе с левой ограничивает интервал, на котором шаг допускает поиск целевой точки

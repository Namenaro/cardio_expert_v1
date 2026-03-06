from dataclasses import dataclass
from typing import List

from CORE import Signal


@dataclass
class PS_Res:
    id: int  # id пазла в базе

    signal: Signal  # сигнал экземпляра на котором ищем точку

    left_coord: float  # левая координата, заданная в настройках шага, которому принадлежит этот PS
    right_coord: float  # правая. Вместе с левой ограничивает интервал, на котором шаг допускает поиск целевой точки

    res_coords: List[float]  # найеденные "особые"(согласно логике пазла) точки

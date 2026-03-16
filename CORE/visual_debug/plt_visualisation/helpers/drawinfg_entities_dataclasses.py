from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from CORE.signal_1d import Signal


class LineStyle(Enum):
    """Стили линий для вертикальных отметок"""
    SOLID = 'solid'
    DASHED = 'dashed'


@dataclass
class SignalInfo:
    """Хранит информацию о сигнале для отрисовки"""
    signal: Signal
    color: str = '#202020'
    name: Optional[str] = None


@dataclass
class VerticalLineInfo:
    """Хранит информацию о вертикальной линии для отрисовки"""
    x: float
    y_min: float
    y_max: float
    color: str = 'red'
    style: LineStyle = LineStyle.SOLID
    label: Optional[str] = None
    sub_label: Optional[str] = None


@dataclass
class VerticalLineGroupInfo:
    """
    Хранит информацию о группе вертикальных линий для отрисовки.
    Все линии группы рисуются одним цветом и имеют одну общую запись в легенде.
    """
    lines: List[VerticalLineInfo]
    color: str
    label: Optional[str] = None


@dataclass
class IntervalInfo:
    """Хранит информацию об интервале для отрисовки"""
    left: float
    right: float
    color: str = 'yellow'
    alpha: Optional[float] = None  # Если None, используется глобальная прозрачность из SignalRenderer
    label: Optional[str] = None


@dataclass
class PointInfo:
    """Хранит информацию о точке для отрисовки"""
    x: float
    y: float
    color: str
    label: Optional[str] = None
    show_label_near_point: bool = False  # Новый флаг
    zorder: int = 5


@dataclass
class SegmentInfo:
    """Хранит информацию об отрезке для отрисовки"""
    x1: float
    y1: float
    x2: float
    y2: float
    color: str
    style: LineStyle = LineStyle.SOLID
    label: Optional[str] = None
    zorder: int = 4

from typing import Optional, List
from CORE.signal_1d import Signal
from CORE.visual_debug.plt_visualisation.helpers.drawinfg_entities_dataclasses import (
    SignalInfo, VerticalLineInfo, VerticalLineGroupInfo,
    IntervalInfo, PointInfo, SegmentInfo, LineStyle
)
from CORE.visual_debug.plt_visualisation.helpers.base_drawer import BasePlotDrawer


class SignalRenderer:
    """
    Хранит контент и умеет рисовать его через BasePlotDrawer.
    """

    def __init__(self):
        self.signals: List[SignalInfo] = []
        self.vertical_lines: List[VerticalLineInfo] = []
        self.vertical_line_groups: List[VerticalLineGroupInfo] = []
        self.intervals: List[IntervalInfo] = []
        self.points: List[PointInfo] = []
        self.segments: List[SegmentInfo] = []

        # Используем композицию вместо наследования
        self._drawer = BasePlotDrawer()

    def add_signal(self, signal: Signal, color='#202020', name: Optional[str] = None):
        self.signals.append(SignalInfo(signal, color, name))

    def add_vertical_line(self, x: float, y_min: float, y_max: float,
                          color: str = 'red', style: LineStyle = LineStyle.SOLID,
                          label: Optional[str] = None, sub_label: Optional[str] = None):
        self.vertical_lines.append(VerticalLineInfo(x, y_min, y_max, color, style, label, sub_label))

    def add_vertical_lines_group(self, lines: List[VerticalLineInfo], color: str,
                                 label: Optional[str] = None):
        group_lines = [
            VerticalLineInfo(x=line.x, y_min=line.y_min, y_max=line.y_max, color=color,
                             style=line.style, label=line.label, sub_label=line.sub_label)
            for line in lines
        ]
        self.vertical_line_groups.append(VerticalLineGroupInfo(group_lines, color, label))

    def add_interval(self, left: float, right: float, color: str = 'yellow',
                     alpha: Optional[float] = None, label: Optional[str] = None):
        self.intervals.append(IntervalInfo(left, right, color, alpha, label))

    def add_point(self, x: float, y: float, color: str = 'red',
                  label: Optional[str] = None, show_label_near_point: bool = False,
                  zorder: int = 5):
        self.points.append(PointInfo(x, y, color, label, show_label_near_point, zorder))

    def add_segment(self, x1: float, y1: float, x2: float, y2: float,
                    color: str = 'blue', style: LineStyle = LineStyle.SOLID,
                    label: Optional[str] = None, zorder: int = 4):
        self.segments.append(SegmentInfo(x1, y1, x2, y2, color, style, label, zorder))

    def draw(self, ax):
        """Рисует все содержимое на указанном ax."""
        self._drawer.draw(
            ax=ax,
            signals=self.signals,
            vertical_lines=self.vertical_lines,
            vertical_line_groups=self.vertical_line_groups,
            intervals=self.intervals,
            points=self.points,
            segments=self.segments
        )

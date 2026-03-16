import random
from typing import Optional, List
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D

from CORE.signal_1d import Signal
from CORE.visual_debug.plt_visualisation.helpers.drawinfg_entities_dataclasses import (
    SignalInfo, VerticalLineInfo, VerticalLineGroupInfo,
    IntervalInfo, PointInfo, SegmentInfo, LineStyle
)


class SignalRenderer:
    """
    Хранит контент и умеет рисовать его на любом ax.
    """

    def __init__(self):
        # Данные для отрисовки
        self.signals: List[SignalInfo] = []
        self.vertical_lines: List[VerticalLineInfo] = []
        self.vertical_line_groups: List[VerticalLineGroupInfo] = []
        self.intervals: List[IntervalInfo] = []
        self.points: List[PointInfo] = []
        self.segments: List[SegmentInfo] = []

        # Настройки миллиметровки
        self.minor_cell_mv = 0.1
        self.minor_cell_sec = 0.04
        self.major_cell_mv = 0.5
        self.major_cell_sec = 0.2
        self.minor_grid_color = "#f4bfbf"
        self.major_grid_color = "#e37373"
        self.intervals_opacity = 0.3
        self.label_x_offset = 0.01
        self.point_label_offset_x = 0.02
        self.point_label_offset_y = 0.05

    # === Методы добавления элементов ===

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

    # === Методы отрисовки ===

    def draw(self, ax: plt.Axes):
        """Рисует все содержимое на указанном ax."""
        ax.clear()

        self._draw_intervals(ax)
        self._draw_signals(ax)
        self._draw_vertical_elements(ax)
        self._draw_segments(ax)
        self._draw_points(ax)

        self._configure_axes(ax)
        self._add_legend(ax)

        ax.figure.canvas.draw_idle()

    def _draw_intervals(self, ax: plt.Axes):
        for interval in self.intervals:
            alpha = interval.alpha if interval.alpha is not None else self.intervals_opacity
            span = ax.axvspan(interval.left, interval.right,
                              alpha=alpha, color=interval.color,
                              label=interval.label)
            span.set_zorder(1)

    def _draw_signals(self, ax: plt.Axes):
        for signal in self.signals:
            ax.plot(signal.signal.time, signal.signal.signal_mv,
                    color=signal.color, label=signal.name, zorder=2)

    def _draw_vertical_elements(self, ax: plt.Axes):
        # Одиночные линии
        for line in self.vertical_lines:
            self._draw_single_vertical_line(ax, line)

        # Группы линий
        for group in self.vertical_line_groups:
            for line in group.lines:
                self._draw_single_vertical_line(ax, line)

    def _draw_single_vertical_line(self, ax: plt.Axes, line: VerticalLineInfo):
        ax.axvline(x=line.x, ymin=line.y_min, ymax=line.y_max,
                   color=line.color, linestyle=line.style.value,
                   zorder=3, alpha=0.8)

        if line.label or line.sub_label:
            self._add_vertical_line_labels(ax, line)

    def _add_vertical_line_labels(self, ax: plt.Axes, line: VerticalLineInfo):
        y_limits = ax.get_ylim()
        y_min_total, y_max_total = y_limits
        y_height = y_max_total - y_min_total

        y_line_min = y_min_total + line.y_min * y_height
        y_line_max = y_min_total + line.y_max * y_height
        y_line_height = y_line_max - y_line_min

        if line.label:
            y_label_pos = y_line_min + y_line_height * (0.5 + random.uniform(0, 0.5))
            ax.text(line.x + self.label_x_offset, y_label_pos, line.label,
                    fontsize=9, color=line.color,
                    verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                              edgecolor='none', alpha=0.7), zorder=4)

        if line.sub_label:
            y_sub_label_pos = y_line_min + y_line_height * random.uniform(0, 0.5)
            ax.text(line.x + self.label_x_offset, y_sub_label_pos, line.sub_label,
                    fontsize=8, color=line.color, style='italic',
                    verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                              edgecolor='none', alpha=0.7), zorder=4)

    def _draw_segments(self, ax: plt.Axes):
        for segment in self.segments:
            ax.plot([segment.x1, segment.x2], [segment.y1, segment.y2],
                    color=segment.color, linestyle=segment.style.value,
                    label=segment.label, zorder=segment.zorder)

    def _draw_points(self, ax: plt.Axes):
        for point in self.points:
            ax.scatter(point.x, point.y, color=point.color, s=50,
                       zorder=point.zorder,
                       label=point.label if point.label and not point.show_label_near_point else None)

            if point.label and point.show_label_near_point:
                ax.text(point.x + self.point_label_offset_x,
                        point.y + self.point_label_offset_y,
                        point.label, fontsize=8, color=point.color,
                        verticalalignment='bottom', horizontalalignment='left',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                  edgecolor='none', alpha=0.7),
                        zorder=point.zorder + 1)

    def _configure_axes(self, ax: plt.Axes):
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, мВ')
        ax.set_aspect(self.minor_cell_sec / self.minor_cell_mv)

        ax.xaxis.set_major_locator(MultipleLocator(self.major_cell_sec))
        ax.xaxis.set_minor_locator(MultipleLocator(self.minor_cell_sec))
        ax.yaxis.set_major_locator(MultipleLocator(self.major_cell_mv))
        ax.yaxis.set_minor_locator(MultipleLocator(self.minor_cell_mv))

        ax.grid(True, 'major', color=self.major_grid_color, zorder=0)
        ax.grid(True, 'minor', color=self.minor_grid_color, linewidth=0.5, zorder=0)

        # 👇 ИСПРАВЛЕНО: используем set_xmargin для отступа справа
        ax.set_xmargin(0.15)  # 15% отступа справа (и слева тоже)

    # 👇 ИЗМЕНЕНИЕ 2: Изменяем метод добавления легенды
    def _add_legend(self, ax: plt.Axes):
        legend_elements = []
        for group in self.vertical_line_groups:
            if group.label:
                legend_elements.append(Line2D([0], [0], color=group.color,
                                              linestyle='-', label=group.label))

        current_handles, current_labels = ax.get_legend_handles_labels()
        all_handles = list(current_handles) + legend_elements

        if all_handles:
            ax.legend(handles=all_handles,
                      bbox_to_anchor=(1.05, 1),  # Справа от графика
                      loc='upper left',  # Якорь легенды
                      borderaxespad=0.)  # Без отступа от границы

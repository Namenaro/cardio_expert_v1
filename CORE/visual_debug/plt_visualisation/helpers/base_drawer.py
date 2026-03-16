import random
from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.lines import Line2D

from CORE.visual_debug.plt_visualisation.helpers.drawinfg_entities_dataclasses import (
    SignalInfo, VerticalLineInfo, VerticalLineGroupInfo,
    IntervalInfo, PointInfo, SegmentInfo, LineStyle
)


class BasePlotDrawer:
    """
    Базовый класс для рисования на matplotlib Axes.
    Содержит общую логику отрисовки всех элементов.
    """

    def __init__(self):
        # Настройки миллиметровки
        self.minor_cell_mv = 0.1
        self.minor_cell_sec = 0.04
        self.major_cell_mv = 0.5
        self.major_cell_sec = 0.2
        self.minor_grid_color = "#f4bfbf"
        self.major_grid_color = "#e37373"

        # Настройки для интервалов
        self.intervals_opacity = 0.3

        # Настройки для подписей вертикальных линий
        self.label_x_offset = 0.01

        # Настройки для подписей точек
        self.point_label_offset_x = 0.02
        self.point_label_offset_y = 0.05

    def draw(self, ax: plt.Axes,
             signals: List[SignalInfo],
             vertical_lines: List[VerticalLineInfo],
             vertical_line_groups: List[VerticalLineGroupInfo],
             intervals: List[IntervalInfo],
             points: List[PointInfo],
             segments: List[SegmentInfo]) -> None:
        """
        Рисует все элементы на указанном Axes.

        Args:
            ax: Объект Axes для отрисовки
            signals: Список сигналов
            vertical_lines: Список одиночных вертикальных линий
            vertical_line_groups: Список групп вертикальных линий
            intervals: Список интервалов
            points: Список точек
            segments: Список отрезков
        """
        ax.clear()

        self._draw_intervals(ax, intervals)
        self._draw_signals(ax, signals)
        self._draw_vertical_elements(ax, vertical_lines, vertical_line_groups)
        self._draw_segments(ax, segments)
        self._draw_points(ax, points)

        self._configure_axes(ax)
        self._add_legend(ax, vertical_line_groups)

        ax.figure.canvas.draw_idle()

    def _draw_intervals(self, ax: plt.Axes, intervals: List[IntervalInfo]) -> None:
        """Рисует интервалы."""
        for interval in intervals:
            alpha = interval.alpha if interval.alpha is not None else self.intervals_opacity
            span = ax.axvspan(interval.left, interval.right,
                              alpha=alpha, color=interval.color,
                              label=interval.label)
            span.set_zorder(1)

    def _draw_signals(self, ax: plt.Axes, signals: List[SignalInfo]) -> None:
        """Рисует сигналы."""
        for signal in signals:
            ax.plot(signal.signal.time, signal.signal.signal_mv,
                    color=signal.color, label=signal.name, zorder=2)

    def _draw_vertical_elements(self, ax: plt.Axes,
                                vertical_lines: List[VerticalLineInfo],
                                vertical_line_groups: List[VerticalLineGroupInfo]) -> None:
        """Рисует вертикальные линии и их группы."""
        # Одиночные линии
        for line in vertical_lines:
            self._draw_single_vertical_line(ax, line)

        # Группы линий
        for group in vertical_line_groups:
            for line in group.lines:
                self._draw_single_vertical_line(ax, line)

    def _draw_single_vertical_line(self, ax: plt.Axes, line: VerticalLineInfo) -> None:
        """Рисует одну вертикальную линию с подписями."""
        ax.axvline(x=line.x, ymin=line.y_min, ymax=line.y_max,
                   color=line.color, linestyle=line.style.value,
                   zorder=3, alpha=0.8)

        if line.label or line.sub_label:
            self._add_vertical_line_labels(ax, line)

    def _add_vertical_line_labels(self, ax: plt.Axes, line: VerticalLineInfo) -> None:
        """Добавляет подписи к вертикальной линии."""
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

    def _draw_segments(self, ax: plt.Axes, segments: List[SegmentInfo]) -> None:
        """Рисует отрезки."""
        for segment in segments:
            ax.plot([segment.x1, segment.x2], [segment.y1, segment.y2],
                    color=segment.color, linestyle=segment.style.value,
                    label=segment.label, zorder=segment.zorder)

    def _draw_points(self, ax: plt.Axes, points: List[PointInfo]) -> None:
        """Рисует точки."""
        for point in points:
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

    def _configure_axes(self, ax: plt.Axes) -> None:
        """Настраивает внешний вид осей."""
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, мВ')
        ax.set_aspect(self.minor_cell_sec / self.minor_cell_mv)

        ax.xaxis.set_major_locator(MultipleLocator(self.major_cell_sec))
        ax.xaxis.set_minor_locator(MultipleLocator(self.minor_cell_sec))
        ax.yaxis.set_major_locator(MultipleLocator(self.major_cell_mv))
        ax.yaxis.set_minor_locator(MultipleLocator(self.minor_cell_mv))

        ax.grid(True, 'major', color=self.major_grid_color, zorder=0)
        ax.grid(True, 'minor', color=self.minor_grid_color, linewidth=0.5, zorder=0)

    def _add_legend(self, ax: plt.Axes, vertical_line_groups: List[VerticalLineGroupInfo]) -> None:
        """Добавляет легенду."""
        legend_elements = []
        for group in vertical_line_groups:
            if group.label:
                legend_elements.append(Line2D([0], [0], color=group.color,
                                              linestyle='-', label=group.label))

        current_handles, current_labels = ax.get_legend_handles_labels()
        all_handles = list(current_handles) + legend_elements

        if all_handles:
            ax.legend(handles=all_handles)

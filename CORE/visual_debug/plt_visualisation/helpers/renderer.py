import random
from typing import Optional, List

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from CORE.signal_1d import Signal
from CORE.visual_debug.plt_visualisation.helpers.drawinfg_entities_dataclasses import SignalInfo, VerticalLineInfo, \
    VerticalLineGroupInfo, IntervalInfo, LineStyle, PointInfo, SegmentInfo


class SignalRenderer:
    """
    Класс, отвечающий только за логику рисования.
    Хранит контент (сигналы, линии, интервалы) и умеет рисовать их на любом ax.
    """

    def __init__(self):
        self.signals: List[SignalInfo] = []
        self.vertical_lines: List[VerticalLineInfo] = []  # Одиночные линии
        self.vertical_line_groups: List[VerticalLineGroupInfo] = []  # Группы линий
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

        # Настройки для интервалов
        self.intervals_opacity = 0.3  # Глобальная прозрачность для интервалов

        # Настройки для подписей вертикальных линий
        self.label_x_offset = 0.01  # Смещение подписи вправо от линии (в координатах данных)
        self.label_random_range = 0.15  # Диапазон случайного смещения по вертикали (в долях от высоты)

    def add_signal(self, signal: Signal, color='#202020', name: Optional[str] = None):
        """Добавляет сигнал для отрисовки."""
        self.signals.append(SignalInfo(signal, color, name))

    def add_vertical_line(self, x: float, y_min: float, y_max: float, color: str = 'red',
                          style: LineStyle = LineStyle.SOLID, label: Optional[str] = None,
                          sub_label: Optional[str] = None):
        """Добавляет одиночную вертикальную линию для отрисовки."""
        self.vertical_lines.append(VerticalLineInfo(x, y_min, y_max, color, style, label, sub_label))

    def add_vertical_lines_group(self, lines: List[VerticalLineInfo], color: str, label: Optional[str] = None):
        """
        Добавляет группу вертикальных линий для отрисовки.
        Все линии группы рисуются одним цветом и имеют одну общую запись в легенде.

        Args:
            lines: Список объектов VerticalLineInfo (их цвета будут проигнорированы)
            color: Цвет для всех линий группы
            label: Метка группы для легенды
        """
        # Создаем копии линий с новым цветом, чтобы не изменять оригиналы
        group_lines = []
        for line in lines:
            # Создаем новую линию с цветом группы, но сохраняем остальные параметры
            group_line = VerticalLineInfo(x=line.x, y_min=line.y_min, y_max=line.y_max, color=color,
                                          style=line.style, label=line.label,
                                          sub_label=line.sub_label)
            group_lines.append(group_line)

        self.vertical_line_groups.append(VerticalLineGroupInfo(group_lines, color, label))

    def add_interval(self, left: float, right: float, color: str = 'yellow', alpha: Optional[float] = None,
                     label: Optional[str] = None):
        """
        Добавляет интервал для отрисовки.

        Args:
            left: Левая граница интервала
            right: Правая граница интервала
            color: Цвет заливки
            alpha: Прозрачность (если None, используется глобальная intervals_opacity)
            label: Подпись для легенды
        """
        self.intervals.append(IntervalInfo(left, right, color, alpha, label))

    def draw(self, ax: plt.Axes):
        """
        Рисует все содержимое на указанном ax.

        Args:
            ax: Объект Axes для отрисовки
        """
        # Очищаем текущий axes
        ax.clear()

        # Сначала рисуем интервалы (чтобы они были на заднем плане)
        for interval_info in self.intervals:
            # Определяем прозрачность
            alpha = interval_info.alpha if interval_info.alpha is not None else self.intervals_opacity

            # Создаем полупрозрачную область во всю высоту графика
            span = ax.axvspan(interval_info.left, interval_info.right, alpha=alpha, color=interval_info.color,
                              label=interval_info.label)

            # Устанавливаем zorder низкий, чтобы интервалы были под сигналами и линиями
            span.set_zorder(1)

        # Затем рисуем сигналы (средний план)
        for signal_info in self.signals:
            time = signal_info.signal.time
            values = signal_info.signal.signal_mv
            ax.plot(time, values, color=signal_info.color, label=signal_info.name, zorder=2)

        # Рисуем одиночные вертикальные линии (передний план) с подписями
        for line_info in self.vertical_lines:
            self._draw_vertical_line(ax, line_info)

        # Рисуем группы вертикальных линий (передний план) с подписями
        # Для групп создаем отдельные элементы для легенды
        legend_elements = []
        for group_info in self.vertical_line_groups:
            # Рисуем все линии группы
            for line_info in group_info.lines:
                self._draw_vertical_line(ax, line_info)

            # Добавляем элемент для легенды группы, если есть метка
            if group_info.label:
                from matplotlib.lines import Line2D
                legend_elements.append(Line2D([0], [0], color=group_info.color, linestyle='-', label=group_info.label))

        # Рисуем отрезки
        for segment_info in self.segments:
            ax.plot([segment_info.x1, segment_info.x2],
                    [segment_info.y1, segment_info.y2],
                    color=segment_info.color,
                    linestyle=segment_info.style.value,
                    label=segment_info.label,
                    zorder=segment_info.zorder)

        # Рисуем точки
        for point_info in self.points:
            # Рисуем саму точку
            ax.scatter(point_info.x, point_info.y,
                       color=point_info.color,
                       s=50,  # размер точки
                       zorder=point_info.zorder,
                       label=point_info.label if point_info.label and not point_info.show_label_near_point else None)

            # Если нужна подпись рядом с точкой
            if point_info.label and point_info.show_label_near_point:
                # Смещение подписи (можно вынести в параметры класса)
                label_offset_x = getattr(self, 'point_label_offset_x', 0.02)
                label_offset_y = getattr(self, 'point_label_offset_y', 0.05)

                # Добавляем подпись справа сверху от точки
                ax.text(point_info.x + label_offset_x, point_info.y + label_offset_y,
                        point_info.label,
                        fontsize=8,
                        color=point_info.color,
                        verticalalignment='bottom',
                        horizontalalignment='left',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                  edgecolor='none', alpha=0.7),
                        zorder=point_info.zorder + 1)

        # Настройка внешнего вида
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, мВ')

        ax.set_aspect(self.minor_cell_sec / self.minor_cell_mv)

        ax.xaxis.set_major_locator(MultipleLocator(self.major_cell_sec))
        ax.xaxis.set_minor_locator(MultipleLocator(self.minor_cell_sec))

        ax.yaxis.set_major_locator(MultipleLocator(self.major_cell_mv))
        ax.yaxis.set_minor_locator(MultipleLocator(self.minor_cell_mv))

        ax.grid(True, 'major', color=self.major_grid_color, zorder=0)
        ax.grid(True, 'minor', color=self.minor_grid_color, linewidth=0.5, zorder=0)

        # Добавляем легенду
        # Собираем все существующие легенды из графиков
        has_labels = (any(s.name for s in self.signals) or
                      any(l.label for l in self.vertical_lines) or
                      any(i.label for i in self.intervals) or
                      legend_elements or
                      any(p.label for p in self.points) or
                      any(s.label for s in self.segments))

        if has_labels:
            # Получаем текущие элементы легенды из графика
            current_handles, current_labels = ax.get_legend_handles_labels()

            # Добавляем элементы групп
            all_handles = list(current_handles) + legend_elements

            if all_handles:
                ax.legend(handles=all_handles)

        # Обновляем отображение
        ax.figure.canvas.draw_idle()

    def _draw_vertical_line(self, ax: plt.Axes, line_info: VerticalLineInfo):
        """
        Рисует вертикальную линию и её подписи.

        Args:
            ax: Объект Axes для отрисовки
            line_info: Информация о вертикальной линии
        """
        # Рисуем вертикальную линию
        ax.axvline(x=line_info.x, ymin=line_info.y_min, ymax=line_info.y_max, color=line_info.color,
                   linestyle=line_info.style.value, zorder=3, alpha=0.8)

        # Добавляем подписи, если они есть
        if line_info.label or line_info.sub_label:
            self._add_vertical_line_labels(ax, line_info)

    def _add_vertical_line_labels(self, ax: plt.Axes, line_info: VerticalLineInfo):
        """
        Добавляет подписи к вертикальной линии со случайным позиционированием.

        Args:
            ax: Объект Axes для отрисовки
            line_info: Информация о вертикальной линии
        """
        # Получаем текущие пределы по y
        y_limits = ax.get_ylim()
        y_min_total, y_max_total = y_limits

        # Вычисляем высоту графика
        y_height = y_max_total - y_min_total

        # Вычисляем позиции для подписей на основе y_min и y_max линии
        y_line_min = y_min_total + line_info.y_min * y_height
        y_line_max = y_min_total + line_info.y_max * y_height
        y_line_height = y_line_max - y_line_min

        # Позиция для главной подписи (верхняя половина линии)
        if line_info.label:
            # Случайная позиция в верхней половине линии (от середины до верха)
            y_label_pos = y_line_min + y_line_height * (0.5 + random.uniform(0, 0.5))

            # Добавляем главную подпись
            ax.text(line_info.x + self.label_x_offset, y_label_pos, line_info.label, fontsize=9, color=line_info.color,
                    verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.7), zorder=4)

        # Позиция для дополнительной подписи (нижняя половина линии)
        if line_info.sub_label:
            # Случайная позиция в нижней половине линии (от низа до середины)
            y_sub_label_pos = y_line_min + y_line_height * random.uniform(0, 0.5)

            # Добавляем дополнительную подпись
            ax.text(line_info.x + self.label_x_offset, y_sub_label_pos, line_info.sub_label, fontsize=8,
                    color=line_info.color, style='italic', verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.7), zorder=4)

    def add_point(self, x: float, y: float, color: str = 'red', label: Optional[str] = None,
                  show_label_near_point: bool = False, zorder: int = 5):
        """
        Добавляет точку для отрисовки.

        Args:
            x: координата x
            y: координата y
            color: цвет точки
            label: текст подписи (если None или show_label_near_point=False, подпись не отображается)
            show_label_near_point: если True, подпись отображается рядом с точкой, а не в легенде
            zorder: порядок отрисовки
        """
        self.points.append(PointInfo(x, y, color, label, show_label_near_point, zorder))

    def add_segment(self, x1: float, y1: float, x2: float, y2: float,
                    color: str = 'blue', style: LineStyle = LineStyle.SOLID,
                    label: Optional[str] = None, zorder: int = 4):
        """Добавляет отрезок для отрисовки."""
        self.segments.append(SegmentInfo(x1, y1, x2, y2, color, style, label, zorder))
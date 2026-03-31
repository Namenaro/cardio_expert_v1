# DA3/simulation_app/visual_debug/plt_visualisation/draw_exemplars_pool.py

from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np

from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug.plt_visualisation import Drawer, LineStyle


class DrawExemplarsPool:
    """Класс для визуализации пула экземпляров с сигналом и ground truth."""

    GROUND_TRUTH_COLOR = '#000000'
    SIGNAL_COLOR = '#0000FF'
    DEFAULT_EXEMPLAR_COLOR = '#808080'

    def __init__(self, pool: Optional[ExemplarsPool] = None,
                 exemplars: Optional[List[Exemplar]] = None,
                 exemplar_colors: Optional[List[str]] = None,
                 padding_percent: float = 20,
                 show_legend: bool = True,
                 x_limits: Optional[Tuple[float, float]] = None):
        """
        Создаёт fig и рисует на нём экземпляры.

        :param pool: объект ExemplarsPool для визуализации (опционально)
        :param exemplars: список экземпляров для визуализации (опционально)
        :param exemplar_colors: список цветов для экземпляров (опционально)
        :param padding_percent: отступ от крайних точек в процентах
        :param show_legend: показывать ли легенду
        :param x_limits: явные границы по X (left, right), если заданы, то padding_percent игнорируется
        """
        if pool is None and exemplars is None:
            raise ValueError("Должен быть указан либо pool, либо exemplars")

        self.pool = pool
        self.exemplars = exemplars
        self.exemplar_colors = exemplar_colors or []
        self.show_legend = show_legend
        self.padding_percent = padding_percent
        self.x_limits = x_limits
        self.fig, self.ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
        self.drawer = Drawer(ax=self.ax)

        # Настройка прозрачности
        self.drawer.renderer.alpha = 0.7

        self.ground_truth: Optional[Exemplar] = None
        self._all_points: List[Tuple[float, float, str, Exemplar]] = []

        # Получаем сигнал
        self._signal = None
        if pool is not None and pool.signal is not None:
            self._signal = pool.signal
        elif exemplars and len(exemplars) > 0:
            self._signal = exemplars[0].get_signal()

    def _get_color_from_score(self, score: Optional[float]) -> str:
        """Возвращает цвет на основе оценки."""
        if score is None:
            return self.DEFAULT_EXEMPLAR_COLOR

        normalized = np.clip(score, 0, 1)
        red = int(255 * (1 - normalized))
        green = int(255 * normalized)
        blue = 0
        return f'#{red:02x}{green:02x}{blue:02x}'

    def _get_sorted_points_from_exemplar(self, exemplar: Exemplar) -> List[Tuple[float, float, str]]:
        """Возвращает отсортированные точки экземпляра."""
        points_with_y = []

        for point_name, (x, track_id) in exemplar._points.items():
            y = exemplar.get_signal().get_amplplitude_in_moment(x)
            if y is not None:
                points_with_y.append((x, y, point_name))
                self._all_points.append((x, y, point_name, exemplar))

        return sorted(points_with_y, key=lambda p: p[0])

    def _calculate_x_limits(self) -> Tuple[float, float]:
        """Рассчитывает границы отображения по оси X с учетом паддинга."""
        if self.x_limits is not None:
            return self.x_limits

        if not self._all_points:
            if self._signal is not None:
                return self._signal.time[0], self._signal.time[-1]
            return 0, 1

        x_coords = [p[0] for p in self._all_points]
        x_min = min(x_coords)
        x_max = max(x_coords)

        interval_length = x_max - x_min
        padding = interval_length * (self.padding_percent / 100)

        x_min_padded = x_min - padding
        x_max_padded = x_max + padding

        if self._signal is not None:
            x_min_padded = max(x_min_padded, self._signal.time[0])
            x_max_padded = min(x_max_padded, self._signal.time[-1])

        return x_min_padded, x_max_padded

    def _add_exemplar_to_drawer(self, exemplar: Exemplar, color: str, label: str,
                                is_ground_truth: bool = False):
        """Добавляет один экземпляр в drawer для отрисовки."""
        points = self._get_sorted_points_from_exemplar(exemplar)

        if not points:
            return

        if len(points) >= 2:
            for i in range(len(points) - 1):
                x1, y1, _ = points[i]
                x2, y2, _ = points[i + 1]
                self.drawer.add_segment(
                    x1=x1, y1=y1,
                    x2=x2, y2=y2,
                    color=color,
                    style=LineStyle.SOLID,
                    label=label if i == 0 else None,
                    zorder=4 if is_ground_truth else 3
                )

        for x, y, point_name in points:
            self.drawer.add_point(
                x=x, y=y,
                color=color,
                label=point_name,
                show_label_near_point=True,
                zorder=5 if is_ground_truth else 4
            )

    def set_ground_truth(self, ground_truth: Optional[Exemplar]):
        """Устанавливает эталонный экземпляр."""
        self.ground_truth = ground_truth

    def get_fig(self):
        """Создает и возвращает фигуру с визуализацией."""
        # Очищаем drawer
        self.drawer.renderer.signals.clear()
        self.drawer.renderer.vertical_lines.clear()
        self.drawer.renderer.vertical_line_groups.clear()
        self.drawer.renderer.intervals.clear()
        self.drawer.renderer.points.clear()
        self.drawer.renderer.segments.clear()

        self._all_points.clear()

        # Добавляем сигнал
        if self._signal is not None:
            self.drawer.add_signal(self._signal, color=self.SIGNAL_COLOR, name='Сигнал ЭКГ')

        # Добавляем ground truth
        if self.ground_truth is not None:
            self._add_exemplar_to_drawer(
                exemplar=self.ground_truth,
                color=self.GROUND_TRUTH_COLOR,
                label='Ground Truth',
                is_ground_truth=True
            )

        # Добавляем экземпляры
        if self.pool is not None and self.pool.exemplars_sorted:
            for i, exemplar in enumerate(self.pool.exemplars_sorted):
                color = self._get_color_from_score(exemplar.evaluation_result)

                if exemplar.evaluation_result is not None:
                    label = f'Экземпляр {i + 1} (оценка: {exemplar.evaluation_result:.2f})'
                else:
                    label = None

                self._add_exemplar_to_drawer(exemplar, color, label)

        elif self.exemplars is not None:
            for i, exemplar in enumerate(self.exemplars):
                if i < len(self.exemplar_colors):
                    color = self.exemplar_colors[i]
                else:
                    color = self.DEFAULT_EXEMPLAR_COLOR
                self._add_exemplar_to_drawer(exemplar, color, None)

        self.drawer.redraw()

        if not self.show_legend:
            legend = self.ax.get_legend()
            if legend is not None:
                legend.remove()

        # Применяем границы
        x_min, x_max = self._calculate_x_limits()
        self.ax.set_xlim(x_min, x_max)
        self.ax.autoscale(enable=False, axis='x')
        self.ax.autoscale(enable=True, axis='y')

        return self.fig
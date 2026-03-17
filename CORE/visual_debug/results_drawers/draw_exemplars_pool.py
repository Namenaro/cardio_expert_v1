import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
import numpy as np

from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug.plt_visualisation import Drawer, LineStyle


class DrawExemplarsPool:
    """Класс для визуализации пула экземпляров с сигналом и ground truth."""

    # Цвета для разных элементов
    GROUND_TRUTH_COLOR = '#000000'  # Черный
    SIGNAL_COLOR = '#0000FF'  # Синий

    def __init__(self, pool: ExemplarsPool, padding_percent: float = 20, show_legend: bool = True):
        """
        Создаёт fig и рисует на нём пул экземпляров.

        :param pool: объект ExemplarsPool для визуализации
        :param padding_percent: отступ от крайних точек в процентах
        :param show_legend: показывать ли легенду
        """
        self.pool = pool
        self.show_legend = show_legend
        self.fig, self.ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
        self.drawer = Drawer(ax=self.ax)
        self.padding_percent = padding_percent

        # Настройка прозрачности для точек и сегментов
        self.drawer.renderer.alpha = 0.7

        # Сохраняем ground truth, если он будет добавлен позже
        self.ground_truth: Optional[Exemplar] = None

        # Точки всех экземпляров для расчета границ
        self._all_points: List[Tuple[float, float, str, Exemplar]] = []

    def _get_color_from_score(self, score: Optional[float]) -> str:
        """Возвращает цвет на основе оценки."""
        if score is None:
            return '#808080'  # Серый для None

        normalized = np.clip(score, 0, 1)
        red = int(255 * (1 - normalized))
        green = int(255 * normalized)
        blue = 0
        return f'#{red:02x}{green:02x}{blue:02x}'

    def _get_sorted_points_from_exemplar(self, exemplar: Exemplar) -> List[Tuple[float, float, str]]:
        """
        Возвращает отсортированные по координате x точки экземпляра с их именами и значениями y.

        :param exemplar: объект Exemplar
        :return: список кортежей (x, y, point_name)
        """
        points_with_y = []

        for point_name, (x, track_id) in exemplar._points.items():
            y = exemplar.get_signal().get_amplplitude_in_moment(x)
            if y is not None:
                points_with_y.append((x, y, point_name))
                self._all_points.append((x, y, point_name, exemplar))

        return sorted(points_with_y, key=lambda p: p[0])

    def _calculate_x_limits(self) -> Tuple[float, float]:
        """
        Рассчитывает границы отображения по оси X с учетом паддинга.

        :return: Tuple (x_min, x_max) - границы для отображения
        """
        if not self._all_points:
            # Если нет точек, используем весь сигнал
            signal = self.pool.signal
            return signal.time[0], signal.time[-1]

        x_coords = [p[0] for p in self._all_points]
        x_min = min(x_coords)
        x_max = max(x_coords)

        interval_length = x_max - x_min
        padding = interval_length * (self.padding_percent / 100)

        x_min_padded = x_min - padding
        x_max_padded = x_max + padding

        # Не выходим за пределы сигнала
        signal = self.pool.signal
        x_min_padded = max(x_min_padded, signal.time[0])
        x_max_padded = min(x_max_padded, signal.time[-1])

        return x_min_padded, x_max_padded

    def _add_exemplar_to_drawer(self, exemplar: Exemplar, color: str, label: str,
                                is_ground_truth: bool = False):
        """
        Добавляет один экземпляр в drawer для отрисовки.

        :param exemplar: объект Exemplar
        :param color: цвет для отрисовки
        :param label: метка для легенды
        :param is_ground_truth: является ли экземпляр эталонным
        """
        points = self._get_sorted_points_from_exemplar(exemplar)

        if not points:
            return

        # Рисуем соединительную линию между соседними точками
        if len(points) >= 2:
            for i in range(len(points) - 1):
                x1, y1, _ = points[i]
                x2, y2, _ = points[i + 1]
                self.drawer.add_segment(
                    x1=x1, y1=y1,
                    x2=x2, y2=y2,
                    color=color,
                    style=LineStyle.SOLID,
                    label=label if i == 0 else None,  # Только первый сегмент в легенду
                    zorder=4 if is_ground_truth else 3
                )

        # Рисуем точки с подписями рядом
        for x, y, point_name in points:
            self.drawer.add_point(
                x=x, y=y,
                color=color,
                label=point_name,
                show_label_near_point=True,
                zorder=5 if is_ground_truth else 4
            )

    def set_ground_truth(self, ground_truth: Optional[Exemplar]):
        """
        Устанавливает эталонный экземпляр для отрисовки.

        :param ground_truth: эталонный экземпляр или None
        """
        self.ground_truth = ground_truth

    def get_fig(self):
        """Создает и возвращает фигуру с визуализацией пула."""
        # Очищаем drawer
        self.drawer.renderer.signals.clear()
        self.drawer.renderer.vertical_lines.clear()
        self.drawer.renderer.vertical_line_groups.clear()
        self.drawer.renderer.intervals.clear()
        self.drawer.renderer.points.clear()
        self.drawer.renderer.segments.clear()

        # Очищаем собранные точки
        self._all_points.clear()

        # Добавляем сигнал
        self.drawer.add_signal(self.pool.signal, color=self.SIGNAL_COLOR, name='Сигнал ЭКГ')

        # Добавляем ground truth если есть
        if self.ground_truth is not None:
            self._add_exemplar_to_drawer(
                exemplar=self.ground_truth,
                color=self.GROUND_TRUTH_COLOR,
                label='Ground Truth',
                is_ground_truth=True
            )

        # Добавляем все экземпляры из пула
        if self.pool.exemplars_sorted:
            for i, exemplar in enumerate(self.pool.exemplars_sorted):
                color = self._get_color_from_score(exemplar.evaluation_result)

                if exemplar.evaluation_result is not None:
                    label = f'Экземпляр {i + 1} (оценка: {exemplar.evaluation_result:.2f})'
                else:
                    label = f'Экземпляр {i + 1} (без оценки)'

                self._add_exemplar_to_drawer(exemplar, color, label)

                # Отрисовываем все элементы
                self.drawer.redraw()

                # Если легенда не нужна - удаляем её
                if not self.show_legend:
                    legend = self.ax.get_legend()
                    if legend is not None:
                        legend.remove()

                # Применяем границы с паддингом
                x_min, x_max = self._calculate_x_limits()
                self.ax.set_xlim(x_min, x_max)
                self.ax.autoscale(enable=False, axis='x')
                self.ax.autoscale(enable=True, axis='y')

                return self.fig

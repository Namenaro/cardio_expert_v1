import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TABLEAU_COLORS
from typing import List, Dict, Optional
import numpy as np

from CORE.visual_debug import StepRes
from CORE.visual_debug.plt_visualisation import Drawer, VerticalLineInfo
from CORE.run import Exemplar


class DrawStepRes:
    def __init__(self, res_obj: StepRes,
                 exemplar_color_map: Optional[Dict[Exemplar, str]] = None,
                 padding_percent: float = 20):
        """
        Создаёт fig и рисует на нём результат работы всех треков шага.
        Каждая группа точек (от одного трека) отображается своим цветом.

        :param res_obj: объект StepRes для визуализации
        :param exemplar_color_map: словарь {exemplar: color} для цветов экземпляров
        :param padding_percent: отступ от интервала поиска в процентах
        """
        self.res = res_obj
        self.exemplar_color_map = exemplar_color_map or {}
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=self.ax)
        self.padding_percent = padding_percent

        # Сохраняем пределы по Y после создания, но до отрисовки
        self.y_min, self.y_max = self.ax.get_ylim()

        # Кэш для цветов треков, связанных с экземплярами
        self._track_color_cache = {}

    def _get_color_for_track(self, track_id: int, exemplar: Optional[Exemplar] = None) -> str:
        """
        Возвращает цвет для трека.
        Если передан экземпляр и для него есть цвет в exemplar_color_map,
        используем этот цвет. Иначе генерируем цвет на основе ID трека.

        :param track_id: ID трека
        :param exemplar: экземпляр, связанный с этим треком
        :return: цвет в формате hex
        """
        # Если есть экземпляр и для него задан цвет, используем его
        if exemplar is not None and exemplar in self.exemplar_color_map:
            return self.exemplar_color_map[exemplar]

        # Если цвет для этого трека уже был сгенерирован, возвращаем его
        if track_id in self._track_color_cache:
            return self._track_color_cache[track_id]

        # Генерируем новый цвет для трека
        color = self._generate_color_from_id(track_id)
        self._track_color_cache[track_id] = color
        return color

    def _generate_color_from_id(self, track_id: int) -> str:
        """
        Генерирует цвет на основе ID трека.
        Использует золотое сечение для равномерного распределения.

        :param track_id: ID трека
        :return: цвет в формате hex
        """
        # Золотое сечение для равномерного распределения цветов
        golden_ratio = 0.618033988749895
        hue = (track_id * golden_ratio) % 1.0
        saturation = 0.7
        value = 0.8

        # Конвертируем HSV в RGB
        import colorsys
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return f'#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}'

    def _get_colors_for_tracks(self, n_colors: int) -> List[str]:
        """
        Генерирует список различных цветов для треков (для обратной совместимости).

        :param n_colors: количество цветов
        :return: список цветов в формате hex
        """
        if n_colors == 0:
            return []

        # Используем предопределенные цвета из таблицы matplotlib
        tableau_colors = list(TABLEAU_COLORS.values())

        if n_colors <= len(tableau_colors):
            return tableau_colors[:n_colors]

        # Если цветов не хватает, создаем градиент
        cmap = LinearSegmentedColormap.from_list(
            "track_colors_gradient",
            ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#D4A5A5", "#9B59B6", "#3498DB"]
        )
        colors = [cmap(i / (n_colors - 1)) for i in range(n_colors)]
        return [self._rgb_to_hex(color) for color in colors]

    @staticmethod
    def _rgb_to_hex(rgb) -> str:
        """Конвертирует RGB кортеж в HEX строку."""
        r, g, b = int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_fig(self):
        # Рассчитываем границы с паддингом
        interval_length = self.res.right_coord - self.res.left_coord
        padding = interval_length * (self.padding_percent / 100)

        left_with_padding = self.res.left_coord - padding
        right_with_padding = self.res.right_coord + padding

        # Рисуем сигнал
        self.drawer.add_signal(signal=self.res.signal, color='black', name="исходный сигнал")

        # Отображаем интервал поиска точки на этом шаге
        self.drawer.add_interval(
            left=self.res.left_coord,
            right=self.res.right_coord,
            color="blue",
            alpha=0.1,
            label="интервал поиска"
        )

        # Получаем экземпляры, созданные в этом шаге
        exemplars = self.res.get_exemplars()

        # Создаем словарь для связи экземпляров с треками
        # Предполагаем, что каждый экземпляр соответствует своему треку
        exemplar_by_track = {}
        if exemplars:
            # Если количество экземпляров соответствует количеству треков
            # или больше, сопоставляем их по порядку
            for idx, exemplar in enumerate(exemplars):
                if idx < len(self.res.tracks_results):
                    track_id = self.res.tracks_results[idx].id
                    exemplar_by_track[track_id] = exemplar

        # Получаем словарь координат точек по ID треков
        tracks_coords_by_id = self.res.get_tracks_results()

        if tracks_coords_by_id:
            # Для обратной совместимости: если нет exemplar_color_map,
            # используем старый метод генерации цветов
            use_old_method = len(self.exemplar_color_map) == 0

            if use_old_method:
                colors = self._get_colors_for_tracks(len(tracks_coords_by_id))
                color_iter = iter(colors)

            # Рисуем точки для каждого трека
            for track_id, coords in tracks_coords_by_id.items():
                if coords:  # Проверяем, что есть координаты для отрисовки
                    # Получаем цвет для трека
                    if use_old_method:
                        color = next(color_iter, "#FF0000")
                    else:
                        exemplar = exemplar_by_track.get(track_id)
                        color = self._get_color_for_track(track_id, exemplar)

                    lines = [
                        VerticalLineInfo(x=x, y_max=self.y_max, y_min=self.y_min)
                        for x in coords
                    ]
                    self.drawer.add_vertical_lines_group(
                        lines=lines,
                        color=color,
                        label=f"Track-{track_id}"
                    )

        # Заполнив все рисуемые сущности, проводим их отрисовку на холст
        self.drawer.redraw()

        # Устанавливаем границы по X с учетом паддинга
        self.ax.set_xlim(left_with_padding, right_with_padding)

        # Отключаем автоматическое масштабирование по X
        self.ax.autoscale(enable=False, axis='x')

        # Автоматическое масштабирование по Y оставляем включенным
        self.ax.autoscale(enable=True, axis='y')

        return self.fig
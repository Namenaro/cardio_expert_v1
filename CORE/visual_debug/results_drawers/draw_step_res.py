import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TABLEAU_COLORS

from CORE.visual_debug import StepRes
from CORE.visual_debug.plt_visualisation import Drawer, VerticalLineInfo


class DrawStepRes:
    def __init__(self, res_obj: StepRes, padding_percent: float = 20):
        """Создаёт fig и рисует на нём результат работы всех треков шага.
        Каждая группа точек (от одного трека) отображается своим цветом."""
        self.res = res_obj
        self.fig, ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=ax, is_user_point_needed=True)
        self.padding_percent = padding_percent
        self.y_min, self.ymax = ax.get_ylim()

    def _get_colors_for_tracks(self, n_colors: int) -> list:
        """Генерирует список различных цветов для треков."""
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
        # Рисуем исходный сигнал — всегда чёрный
        old_signal = self.res.signal.get_cropped_with_padding(
            coord_left=self.res.left_coord,
            coord_right=self.res.right_coord,
            padding_percent=self.padding_percent
        )
        self.drawer.add_signal(signal=old_signal, color='black', name="исходный сигнал")

        # Отображаем интервал поиска точки на этом шаге
        self.drawer.add_interval(
            left=self.res.left_coord,
            right=self.res.right_coord,
            color="blue",
            alpha=0.1
        )

        # Получаем словарь координат точек по ID треков
        tracks_coords_by_id = self.res.get_tracks_results()

        if tracks_coords_by_id:
            # Генерируем цвета для каждого трека
            colors = self._get_colors_for_tracks(len(tracks_coords_by_id))

            # Рисуем точки для каждого трека своим цветом
            for (track_id, coords), color in zip(tracks_coords_by_id.items(), colors):
                if coords:  # Проверяем, что есть координаты для отрисовки
                    lines = [
                        VerticalLineInfo(x=x, y_max=self.ymax, y_min=self.y_min)
                        for x in coords
                    ]
                    self.drawer.add_vertical_lines_group(
                        lines=lines,
                        color=color,
                        label=f"Track-{track_id}"
                    )

        # Заполнив все рисуемые сущности, проводим их отрисовку на холст
        self.drawer.redraw()
        return self.fig

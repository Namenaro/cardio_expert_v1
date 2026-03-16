import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TABLEAU_COLORS

from CORE.visual_debug import TrackRes
from CORE.visual_debug.plt_visualisation import Drawer, VerticalLineInfo


class DrawTrackRes:
    def __init__(self, res_obj: TrackRes, padding_percent: float = 20):
        """Создаёт fig и рисует на нём результат работы PS-объектов трека.
        Каждая группа точек (от одного PS) отображается своим цветом."""
        self.res = res_obj
        self.fig, ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=ax)
        self.padding_percent = padding_percent
        self.y_min, self.ymax = ax.get_ylim()

    def _get_colors_for_ps(self, n_colors: int) -> list:
        """Генерирует список различных цветов для PS-объектов."""
        if n_colors == 0:
            return []

        # Используем предопределенные цвета из таблицы matplotlib
        tableau_colors = list(TABLEAU_COLORS.values())

        if n_colors <= len(tableau_colors):
            return tableau_colors[:n_colors]

        # Если цветов не хватает, создаем градиент
        cmap = LinearSegmentedColormap.from_list(
            "ps_colors_gradient",
            ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
        )
        colors = [cmap(i / (n_colors - 1)) for i in range(n_colors)]
        return [self._rgb_to_hex(color) for color in colors]

    @staticmethod
    def _rgb_to_hex(rgb) -> str:
        """Конвертирует RGB кортеж в HEX строку."""
        r, g, b = int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_fig(self):
        # Рисуем исходный сигнал до модификаций — всегда чёрный
        old_signal = self.res.signal.get_cropped_with_padding(
            coord_left=self.res.left_coord,
            coord_right=self.res.right_coord,
            padding_percent=self.padding_percent
        )
        self.drawer.add_signal(signal=old_signal, color='black', name="исходный сигнал")

        # Отображаем интервал поиска точки на этом шаге (к которому принадлежит трек)
        self.drawer.add_interval(
            left=self.res.left_coord,
            right=self.res.right_coord,
            color="blue",
            alpha=0.1
        )

        # Получаем словарь координат по ID PS-объектов
        ps_coords_by_id = self.res.get_ps_coords_by_id()

        if ps_coords_by_id:
            # Генерируем цвета для каждого PS-объекта
            colors = self._get_colors_for_ps(len(ps_coords_by_id))

            # Рисуем точки для каждого PS-объекта своим цветом
            for (ps_id, coords), color in zip(ps_coords_by_id.items(), colors):
                if coords:  # Проверяем, что есть координаты для отрисовки
                    lines = [
                        VerticalLineInfo(x=x, y_max=self.ymax, y_min=self.y_min)
                        for x in coords
                    ]
                    self.drawer.add_vertical_lines_group(
                        lines=lines,
                        color=color,
                        label=f"PS-{ps_id}"
                    )

        # Заполнив все рисуемые сущности, проводим их отрисовку на холст
        self.drawer.redraw()
        return self.fig

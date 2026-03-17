import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import List

from CORE.visual_debug import TrackRes
from CORE.visual_debug.plt_visualisation import Drawer


class DrawTrackRes_SM:
    def __init__(self, res_obj: TrackRes, padding_percent: float = 20):
        """Создаёт fig и рисует на нём результат запуска последовательно всех SM этого трека.
        Обеспечивает обработчик нажатия по фигуре — откроет более подробное окно с панелью навигации (увеличение, сдвиг и т. д.)"""
        self.res = res_obj
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=self.ax)
        self.padding_percent = padding_percent

        # Сохраняем пределы по Y после создания, но до отрисовки
        self.y_min, self.y_max = self.ax.get_ylim()

    def _get_gradient_colors(self, n_colors: int) -> List[str]:
        """Генерирует градиент цветов из монотонной гаммы (от синего к фиолетовому)."""
        if n_colors == 0:
            return []
        if n_colors == 1:
            return ['#4169E1']  # тёмно-синий

        # Создаём градиент от синего к фиолетовому
        cmap = LinearSegmentedColormap.from_list(
            "blue_purple_gradient",
            ["#4169E1", "#8A2BE2"]  # Navy Blue → Blue Violet
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

        # ВАЖНО: НЕ обрезаем сигнал, берем весь сигнал
        self.drawer.add_signal(signal=self.res.signal, color='black', name="исходный сигнал")

        # Проверяем, есть ли вообще SM-результаты
        if self.res.sm_res_objs:
            n_intermediate = len(self.res.sm_res_objs) - 1

            # Получаем градиент цветов для промежуточных сигналов
            gradient_colors = self._get_gradient_colors(n_intermediate)

            # Рисуем все стадии редактирования кроме последнего шага с градиентными цветами
            for i, sm_res in enumerate(self.res.sm_res_objs[:-1]):
                # ВАЖНО: НЕ обрезаем сигнал, берем полный результат SM
                self.drawer.add_signal(
                    signal=sm_res.result_signal,
                    color=gradient_colors[i] if gradient_colors else 'gray',
                    name=f"SM-{sm_res.id}"
                )

            # Рисуем результат последнего шага модификации сигнала — всегда зелёный
            self.drawer.add_signal(
                signal=self.res.sm_res_objs[-1].result_signal,
                color='green',
                name="новый сигнал"
            )

        # Отображаем интервал поиска точки на этом шаге (к которому принадлежит трек)
        self.drawer.add_interval(
            left=self.res.left_coord,
            right=self.res.right_coord,
            color="blue",
            alpha=0.1,
            label="интервал поиска"
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
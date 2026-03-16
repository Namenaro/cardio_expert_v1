import matplotlib.pyplot as plt
from typing import List, Tuple

from CORE.run import Exemplar
from CORE.visual_debug.plt_visualisation import Drawer
from CORE.visual_debug.plt_visualisation.helpers.drawinfg_entities_dataclasses import LineStyle


class DrawExemplar:
    def __init__(self, res_obj: Exemplar, padding_percent: float = 20, color: str = 'green'):
        """
        Создаёт fig и рисует на нём экземпляр формы с точками и соединяющей их ломаной линией.

        :param res_obj: объект Exemplar для визуализации
        :param padding_percent: отступ от крайних точек в процентах
        :param color: цвет для отрисовки точек и соединительной линии
        """
        self.res = res_obj
        self.fig, ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=ax, is_user_point_needed=True)
        self.padding_percent = padding_percent
        self.color = color
        self.y_min, self.ymax = ax.get_ylim()

    def _get_sorted_points(self) -> List[Tuple[float, float, str]]:
        """
        Возвращает отсортированные по координате x точки с их именами и значениями y.

        :return: список кортежей (x, y, point_name)
        """
        points_with_y = []

        for point_name, (x, track_id) in self.res._points.items():
            # Получаем амплитуду в точке
            y = self.res.signal.get_amplplitude_in_moment(x)
            if y is not None:  # Игнорируем точки вне сигнала
                points_with_y.append((x, y, point_name))

        # Сортируем по x координате
        return sorted(points_with_y, key=lambda p: p[0])

    def get_fig(self):
        # Определяем границы отображения с учетом отступа
        points = self._get_sorted_points()

        if points:
            x_coords = [p[0] for p in points]
            min_x = min(x_coords)
            max_x = max(x_coords)
            padding = (max_x - min_x) * self.padding_percent / 100
            left_coord = min_x - padding
            right_coord = max_x + padding
        else:
            # Если точек нет, используем центр сигнала с отступом
            signal_duration = self.res.signal.time[-1] - self.res.signal.time[0]
            center = self.res.signal.time[0] + signal_duration / 2
            padding = signal_duration * self.padding_percent / 200
            left_coord = center - padding
            right_coord = center + padding

        # Рисуем исходный сигнал — всегда чёрный
        old_signal = self.res.signal.get_cropped_with_padding(
            coord_left=left_coord,
            coord_right=right_coord,
            padding_percent=0  # Дополнительный отступ не нужен, мы уже учли его выше
        )
        self.drawer.add_signal(signal=old_signal, color='black', name="исходный сигнал")

        # Рисуем точки и соединительную линию
        if len(points) >= 2:
            # Рисуем соединительную линию между соседними точками
            for i in range(len(points) - 1):
                x1, y1, _ = points[i]
                x2, y2, _ = points[i + 1]
                self.drawer.add_segment(
                    x1=x1, y1=y1,
                    x2=x2, y2=y2,
                    color=self.color,
                    style=LineStyle.SOLID,
                    label="соединительная линия" if i == 0 else None  # Только первая линия в легенду
                )

        # Рисуем точки с подписями рядом (не в легенде)
        for x, y, point_name in points:
            self.drawer.add_point(
                x=x, y=y,
                color=self.color,
                label=point_name,  # Имя точки для подписи
                show_label_near_point=True  # Важно! Отображать как подпись рядом
            )

        # Заполнив все рисуемые сущности, проводим их отрисовку на холст
        self.drawer.redraw()
        return self.fig

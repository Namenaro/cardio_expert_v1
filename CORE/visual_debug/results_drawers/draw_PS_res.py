import sys
from math import sin
from typing import Optional, List

import matplotlib.pyplot as plt

from CORE import Signal
from CORE.visual_debug import PS_Res
from CORE.visual_debug.plt_visualisation import Drawer, VerticalLineInfo


class DrawPS_Res:
    """ Создает fig и рисует на нем результат запуска PS, упакованный в PS_Res.
                Обеспечивает обработчик нажатия по фигуре - откроет более подробное окно с панелью навигации (увеличение, сдвиг и т.д.)"""

    def __init__(self, ps_res_obj: PS_Res, padding_procents: float = 20, ground_true_point: Optional[float] = None):
        """

        :param ps_res_obj: объект с результатом отработки PS на фрагменте сигнала
        :param padding_procents: процент длины интервала, который мы отступаем влево и вправо от краев интервала, чтобы показать чуть больше, чем только интервал поиска этой точки
        :param ground_true_point: правильная точка из датасета для этого шага
        """
        self.ps_res = ps_res_obj
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=self.ax)
        self.padding_procents = padding_procents
        self.ground_true_point = ground_true_point

        # Сохраняем пределы по Y после создания, но до отрисовки
        self.y_min, self.y_max = self.ax.get_ylim()

    def get_fig(self):
        # Рассчитываем границы с паддингом
        interval_length = self.ps_res.right_coord - self.ps_res.left_coord
        padding = interval_length * (self.padding_procents / 100)

        left_with_padding = self.ps_res.left_coord - padding
        right_with_padding = self.ps_res.right_coord + padding

        # ВАЖНО: НЕ обрезаем сигнал, берем весь сигнал
        self.drawer.add_signal(signal=self.ps_res.signal, color='black', name="исходный сигнал")

        # Добавляем интервал поиска
        self.drawer.add_interval(
            left=self.ps_res.left_coord,
            right=self.ps_res.right_coord,
            color="blue",
            alpha=0.1,
            label="интервал поиска"
        )

        # Добавляем точки, найденные нашим PS
        if self.ps_res.res_coords:
            lines = [VerticalLineInfo(x=x, y_max=self.y_max, y_min=self.y_min) for x in self.ps_res.res_coords]
            self.drawer.add_vertical_lines_group(lines=lines, color="green", label="найденные точки")

        # Если известна верная точка для этого шага, то тоже рисуем
        if self.ground_true_point is not None:
            self.drawer.add_vertical_line(
                x=self.ground_true_point,
                y_max=self.y_max,
                y_min=self.y_min,
                color="black",
                label="true точка"
            )

        # Отрисовываем все элементы
        self.drawer.redraw()

        # Устанавливаем границы по X с учетом паддинга
        self.ax.set_xlim(left_with_padding, right_with_padding)

        # Отключаем автоматическое масштабирование по X
        self.ax.autoscale(enable=False, axis='x')

        # Автоматическое масштабирование по Y оставляем включенным
        self.ax.autoscale(enable=True, axis='y')

        return self.fig


if __name__ == "__main__":
    from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget)
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Визуализация сигнала")
            self.setGeometry(100, 100, 800, 600)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Создание тестового сигнала
            raw_signal = [sin(i) for i in range(80)]
            test_signal = Signal(signal_mv=raw_signal, frequency=2)
            print(f"Длительность сигнала: {test_signal.get_duration():.2f} секунд")
            print("Сигнал (первые 10 точек):", test_signal.signal_mv[:10])
            print("Время (первые 10 точек):", test_signal.time[:10])

            # Создание тестового PS_Res
            test_ps_res = PS_Res(
                id=1,
                signal=test_signal,
                left_coord=10.0,
                right_coord=14.0,
                res_coords=[11.0, 12.0]
            )

            # Создание визуализатора
            draw_ps_res = DrawPS_Res(ps_res_obj=test_ps_res, ground_true_point=10.1, padding_procents=20)
            fig = draw_ps_res.get_fig()

            # Встраивание matplotlib figure в PySide
            self.canvas = FigureCanvas(fig)

            # Динамическое добавление атрибута ради того, чтобы обработчики кликов из drawer жили столько, сколько canvas
            self.canvas.drawer = draw_ps_res.drawer

            layout.addWidget(self.canvas)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()
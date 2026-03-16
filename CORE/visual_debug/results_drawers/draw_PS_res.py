import sys
from math import sin
from typing import Optional

import matplotlib.pyplot as plt

from CORE import Signal
from CORE.visual_debug import PS_Res
from CORE.visual_debug.plt_visualisation import Drawer, VerticalLineInfo


class DrawPS_Res:
    """ Создает fig и рисует на нем результат запуска PS, упакованный в PS_Res.
                Обеспечивает обработчик нажатия по фигуре - откроет более подробное окно с панелью навигации (увеличение, сдвиг и т.д.)"""

    def __init__(self, ps_res_obj: PS_Res, padding_procents: float = 20, ground_true_point: Optional = None):
        """

        :param ps_res_obj: объект с результатом отработки PS на фрагменте сигнала
        :param padding_procents: процент длины инстервала, который мы отстпаем влево и вправо от краних интервала, чтобы показать чуть больше, чем только интервал поиска этой точки
        :param ground_true_point: правильная точка из датасета для этого шага
        """
        self.ps_res = ps_res_obj
        self.fig, ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=ax, is_user_point_needed=True)
        self.padding_procents = padding_procents
        self.y_min, self.ymax = ax.get_ylim()
        self.ground_true_point = ground_true_point

    def get_fig(self):
        cropped_signal = self.ps_res.signal.get_cropped_with_padding(
            coord_left=self.ps_res.left_coord,
            coord_right=self.ps_res.right_coord,
            padding_percent=self.padding_procents
        )
        self.drawer.add_signal(signal=cropped_signal, color='black', name="исходный сигнал")

        self.drawer.add_interval(left=self.ps_res.left_coord, right=self.ps_res.right_coord, color="blue", alpha=0.1)

        # Добавим точки, найденные нашим PS
        lines = [VerticalLineInfo(x=x, y_max=self.ymax, y_min=self.y_min) for x in self.ps_res.res_coords]
        self.drawer.add_vertical_lines_group(lines=lines, color="green", label="найденные точки")

        # Если измвестна верная точка для этого шага, то их тоже рисуем
        if self.ground_true_point:
            self.drawer.add_vertical_line(x=self.ground_true_point, y_max=self.ymax, y_min=self.y_min, color="black",
                                          label="true")


        self.drawer.redraw()

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
            draw_ps_res = DrawPS_Res(ps_res_obj=test_ps_res, ground_true_point=10.1)
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

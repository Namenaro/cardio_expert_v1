import sys
from math import sin

import matplotlib.pyplot as plt

from CORE import Signal
from CORE.visual_debug import SM_Res
from CORE.visual_debug.plt_visualisation import Drawer


class DrawSM_Res:
    def __init__(self, res_obj: SM_Res, padding_procents: float = 20):
        """ Создает fig и рисует на нем результат запуска SM, упакованный в SM_Res.
         Обеспечивает обработчик нажатия по фигуре - откроет более подробное окно с панелью навигации (увеличение, сдвиг и т.д.)"""

        self.res = res_obj
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=self.ax)
        self.padding_procents = padding_procents

    def get_fig(self):
        # Рассчитываем границы с паддингом
        interval_length = self.res.right_coord - self.res.left_coord
        padding = interval_length * (self.padding_procents / 100)

        left_with_padding = self.res.left_coord - padding
        right_with_padding = self.res.right_coord + padding

        # ВАЖНО: НЕ обрезаем сигнал, берем весь сигнал
        # Просто потом установим границы отображения
        self.drawer.add_signal(signal=self.res.old_signal, color='black', name='исходный сигнал')

        # Добавляем интервал (рисуется на всю высоту графика)
        self.drawer.add_interval(
            left=self.res.left_coord,
            right=self.res.right_coord,
            color="blue",
            alpha=0.1,
            label="интервал обработки"
        )

        # Добавляем новый сигнал (тоже весь)
        self.drawer.add_signal(signal=self.res.result_signal, color='green', name="новый сигнал")

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

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Создание тестового сигнала
            raw_signal = [sin(i) for i in range(80)]
            test_signal = Signal(signal_mv=raw_signal, frequency=2)

            new_raw = [-2 * sin(i) for i in range(80)]
            new_signal = Signal(signal_mv=new_raw, frequency=2)

            # Создание тестового SM_Res
            test_res = SM_Res(
                id=1,
                old_signal=test_signal,
                left_coord=10.0,
                right_coord=14.0,
                result_signal=new_signal
            )

            # Создание визуализатора
            draw_ps_res = DrawSM_Res(res_obj=test_res, padding_procents=20)
            fig = draw_ps_res.get_fig()

            # Встраивание matplotlib figure в PySide
            self.canvas = FigureCanvas(fig)
            self.canvas.drawer = draw_ps_res.drawer
            layout.addWidget(self.canvas)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()
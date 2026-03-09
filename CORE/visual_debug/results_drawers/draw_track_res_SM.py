import sys
from math import sin

import matplotlib.pyplot as plt

from CORE import Signal
from CORE.visual_debug import SM_Res, TrackRes
from CORE.visual_debug.plt_visualisation import Drawer


class DrawTrackRes_SM:
    def __init__(self, res_obj: TrackRes, padding_procents: float = 20):
        """ Создает fig и рисует на нем результат запуска последовательно всех SM этого трека.
         Обеспечивает обработчик нажатия по фигуре - откроет более подробное окно с панелью навигации (увеличение, сдвиг и т.д.)"""

        self.res = res_obj
        self.fig, ax = plt.subplots(figsize=(10, 4))
        self.drawer = Drawer(ax=ax, is_user_point_needed=True)
        self.padding_procents = padding_procents
        self.y_min, self.ymax = ax.get_ylim()

    def get_fig(self):
        # Рисуем исходный сигнал до модификаций
        old_signal = self.res.signal.get_cropped_with_padding(
            coord_left=self.res.left_coord,
            coord_right=self.res.right_coord,
            padding_percent=self.padding_procents
        )
        self.drawer.add_signal(signal=old_signal, color='black', name="исходный сигнал")

        # Проверяем, есть ли вообще SM-результаты
        if self.res.sm_res_objs:
            # Рисуем все стадии редктирвоания кроме последнего шага
            for sm_res in self.res.sm_res_objs[:-1]:
                cropped_signal = sm_res.result_signal.get_cropped_with_padding(
                    coord_left=self.res.left_coord,
                    coord_right=self.res.right_coord,
                    padding_percent=self.padding_procents
                )
                self.drawer.add_signal(signal=cropped_signal, color='black', name=str(sm_res.id))

            # Рисуем результат последнего шага модификации сигнала
            cropped_new = self.res.sm_res_objs[-1].result_signal.get_cropped_with_padding(
                coord_left=self.res.left_coord,
                coord_right=self.res.right_coord,
                padding_percent=self.padding_procents
            )
            self.drawer.add_signal(signal=cropped_new, color='green', name="новый сигнал")

        # Отображаем интервал поиска точки на этом шаге (к которому принадлежит трек)
        self.drawer.add_interval(left=self.res.left_coord, right=self.res.right_coord, color="blue", alpha=0.1)

        # Заполнив все рисуемые сущности, проводим их отрисовку на холст
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

            new_raw = [-2 * sin(i) for i in range(80)]
            new_signal = Signal(signal_mv=new_raw, frequency=2)

            print(f"Длительность сигнала: {test_signal.get_duration():.2f} секунд")
            print("Сигнал (первые 10 точек):", test_signal.signal_mv[:10])
            print("Время (первые 10 точек):", test_signal.time[:10])

            # Создание тестового PS_Res
            test_res = SM_Res(
                id=1,
                old_signal=test_signal,
                left_coord=10.0,
                right_coord=14.0,
                result_signal=new_signal

            )

            # Создание визуализатора
            draw_ps_res = DrawSM_Res(res_obj=test_res)
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

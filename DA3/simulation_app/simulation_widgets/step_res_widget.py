import sys
from math import sin

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.visual_debug import StepRes
from CORE.visual_debug import TrackRes, PS_Res
from CORE.visual_debug.results_drawers.draw_step_res import DrawStepRes


class StepResWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.step_res_obj = None
        self.draw_step_res = None
        self.figure = None
        self.ax = None
        self.canvas = None
        self.init_ui()

    def init_ui(self):
        # Основной layout виджета
        layout = QVBoxLayout(self)

        # Текстовое поле для ID шага
        self.id_text_edit = QTextEdit()
        self.id_text_edit.setMaximumHeight(50)
        self.id_text_edit.setReadOnly(True)
        layout.addWidget(QLabel("ID шага (StepRes):"))
        layout.addWidget(self.id_text_edit)

        # Канвас для визуализации
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def clear(self):
        """Очищает график перед загрузкой новых данных"""
        if self.ax:
            self.ax.clear()
        # Обнуляем ссылку на старый drawer
        self.draw_step_res = None
        self.step_res_obj = None

    def reset_data(self, step_res: StepRes):
        """Заполняет канвас на основе StepRes и записывает ID в текстовое поле."""
        self.step_res_obj = step_res

        # Обновляем текстовое поле с ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(step_res.id))

        # Создаём визуализатор и получаем фигуру
        self.draw_step_res = DrawStepRes(res_obj=step_res)
        updated_fig = self.draw_step_res.get_fig()

        # Заменяем текущую фигуру на обновлённую
        old_figure = self.canvas.figure
        self.canvas.figure = updated_fig

        # Закрываем старую фигуру
        if old_figure is not None and old_figure != updated_fig:
            plt.close(old_figure)

        self.canvas.draw()

    def cleanup(self):
        """Очищает ресурсы matplotlib"""
        if self.canvas:
            self.canvas.deleteLater()
        if self.figure:
            plt.close(self.figure)
        self.figure = None
        self.ax = None
        self.canvas = None
        self.draw_step_res = None
        self.step_res_obj = None


if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Визуализация StepRes с несколькими треками")
            self.setGeometry(100, 100, 800, 600)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Создание тестового сигнала
            initial_signal = Signal(signal_mv=[0.1 - sin(i) for i in range(80)], frequency=2)

            # Создаём PS объекты для первого трека
            ps_res_list_track1 = [
                PS_Res(
                    id=1,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[11.2, 12.5]  # две точки для первого PS первого трека
                ),
                PS_Res(
                    id=2,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[13.2, 14.5]  # две точки для второго PS первого трека
                )
            ]

            # Создаём PS объекты для второго трека
            ps_res_list_track2 = [
                PS_Res(
                    id=3,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[10.5, 11.8]  # две точки для первого PS второго трека
                ),
                PS_Res(
                    id=4,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[12.0, 13.8]  # две точки для второго PS второго трека
                )
            ]

            # Создаём треки
            track1 = TrackRes(
                id=101,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                ps_res_objs=ps_res_list_track1,
                sm_res_objs=[]  # пустой список для совместимости
            )

            track2 = TrackRes(
                id=102,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                ps_res_objs=ps_res_list_track2,
                sm_res_objs=[]  # пустой список для совместимости
            )

            # Создаём StepRes с двумя треками
            test_step_res = StepRes(
                id=42,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                tracks_results=[track1, track2]
            )

            # Создание виджета StepResWidget
            self.step_res_widget = StepResWidget()

            # Заполняем виджет данными из тестового StepRes
            self.step_res_widget.reset_data(test_step_res)

            # Добавляем виджет в layout
            layout.addWidget(self.step_res_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()

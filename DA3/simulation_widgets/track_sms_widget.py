import sys
from math import sin

import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QApplication, QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.visual_debug import SM_Res, TrackRes
from CORE.visual_debug.results_drawers.draw_track_res_SM import DrawTrackRes_SM


class TrackResWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Основной layout виджета
        layout = QVBoxLayout(self)

        # Текстовое поле для ID
        self.id_text_edit = QTextEdit()
        self.id_text_edit.setMaximumHeight(50)
        self.id_text_edit.setReadOnly(True)
        layout.addWidget(QLabel("ID трека (TrackRes):"))
        layout.addWidget(self.id_text_edit)

        # Канвас для визуализации
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Хранилище для объекта TrackRes и Drawer
        self.track_res_obj = None
        self.draw_track_res = None

    def reset_result_object(self, track_res: TrackRes):
        """Заполняет канвас на основе TrackRes и записывает ID в текстовое поле."""
        self.track_res_obj = track_res

        # Обновляем текстовое поле с ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(track_res.id))

        # Очищаем фигуру перед перерисовкой
        self.ax.clear()

        # Создаём визуализатор и получаем фигуру
        self.draw_track_res = DrawTrackRes_SM(res_obj=track_res)
        updated_fig = self.draw_track_res.get_fig()

        # Заменяем текущую фигуру на обновлённую
        self.canvas.figure = updated_fig
        self.canvas.draw()


if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Визуализация TrackRes")
            self.setGeometry(100, 100, 800, 600)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Создание тестовых SM_Res объектов

            initial_signal = Signal(signal_mv=[0.1 - sin(i) for i in range(80)], frequency=2)

            # Генерируем все сигналы сразу
            all_signals = [initial_signal] + [
                Signal(signal_mv=[sin(j) + (i + 1) * 0.1 for j in range(80)], frequency=2)
                for i in range(4)
            ]

            # Создаём SM_Res-ы
            sm_res_list = [
                SM_Res(
                    id=i + 1,
                    old_signal=all_signals[i],
                    result_signal=all_signals[i + 1],
                    left_coord=10.0,
                    right_coord=14.0
                )
                for i in range(4)
            ]

            test_track_res = TrackRes(
                id=42,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                ps_res_objs=[],
                sm_res_objs=sm_res_list
            )
            # Создание виджета TrackResWidget
            self.track_res_widget = TrackResWidget()

            # Заполняем виджет данными из тестового TrackRes
            self.track_res_widget.reset_result_object(test_track_res)

            # Добавляем виджет в layout
            layout.addWidget(self.track_res_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()

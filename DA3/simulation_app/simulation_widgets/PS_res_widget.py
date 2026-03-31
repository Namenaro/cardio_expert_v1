import sys
from math import sin
from typing import Optional

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QLabel, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.visual_debug import PS_Res
from CORE.visual_debug.results_drawers.draw_PS_res import DrawPS_Res


class PS_ResWidget(QWidget):
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
        layout.addWidget(QLabel("ID объекта PS_Res:"))
        layout.addWidget(self.id_text_edit)

        # Канвас для визуализации
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Хранилище для объекта PS_Res и Drawer
        self.ps_res_obj = None
        self.draw_ps_res = None

    def reset_data(self, ps_res: PS_Res, ground_true_point: Optional[float] = None):
        """Заполняет канвас на основе PS_Res и записывает ID в текстовое поле.
        :param ps_res объект с результатом запуска ps
        :param ground_true_point правильная координата точки этого шага, из датасета (опционально)"""
        self.ps_res_obj = ps_res

        # Обновляем текстовое поле с ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(ps_res.id))

        # Очищаем фигуру перед перерисовкой
        self.ax.clear()

        # Создаём визуализатор и получаем фигуру
        self.draw_ps_res = DrawPS_Res(ps_res_obj=ps_res, ground_true_point=ground_true_point)
        updated_fig = self.draw_ps_res.get_fig()

        # Заменяем текущую фигуру на обновлённую
        self.canvas.figure = updated_fig
        self.canvas.draw()


if __name__ == "__main__":
    from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget)


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

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

            # Создание виджета RS_res_widget
            self.rs_res_widget = PS_ResWidget()

            # Заполняем виджет данными из тестового PS_Res
            self.rs_res_widget.reset_data(test_ps_res, ground_true_point=10.55)

            # Добавляем виджет в layout
            layout.addWidget(self.rs_res_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()

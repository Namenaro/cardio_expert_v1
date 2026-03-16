import sys
from math import sin

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QLabel, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.visual_debug import SM_Res
from CORE.visual_debug.results_drawers.draw_SM_res import DrawSM_Res


class SM_ResWidget(QWidget):
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
        layout.addWidget(QLabel("ID объекта SM_Res:"))
        layout.addWidget(self.id_text_edit)

        # Канвас для визуализации
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Хранилище для объекта SM_Res и Drawer
        self.ps_res_obj = None
        self.draw_sm_res = None

    def reset_data(self, sm_res: SM_Res):
        """Заполняет канвас на основе PS_Res и записывает ID в текстовое поле.
        :param ps_res объект с результатом запуска ps
        :param ground_true_point правильная координата точки этого шага, из датасета (опционально)"""
        self.sm_res_obj = sm_res

        # Обновляем текстовое поле с ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(sm_res.id))

        # Очищаем фигуру перед перерисовкой
        self.ax.clear()

        # Создаём визуализатор и получаем фигуру
        self.draw_ps_res = DrawSM_Res(res_obj=sm_res)
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

            test_signal = Signal(signal_mv=[sin(i) for i in range(80)], frequency=2)
            test_signal_2 = Signal(signal_mv=[sin(i) - 0.1 for i in range(80)], frequency=2)
            print(f"Длительность сигнала: {test_signal.get_duration():.2f} секунд")
            print("Сигнал (первые 10 точек):", test_signal.signal_mv[:10])
            print("Время (первые 10 точек):", test_signal.time[:10])

            # Создание тестового PS_Res
            test_sm_res = SM_Res(
                id=1,
                old_signal=test_signal,
                left_coord=10.0,
                right_coord=14.0,
                result_signal=test_signal_2
            )

            # Создание виджета
            self.rs_res_widget = SM_ResWidget()

            # Заполняем виджет данными из тестового SM_Res
            self.rs_res_widget.reset_data(test_sm_res)

            # Добавляем виджет в layout
            layout.addWidget(self.rs_res_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()

import sys
from math import sin
from typing import Dict, List, Tuple, Optional, Any

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QApplication, QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.run import Exemplar

from CORE.visual_debug.results_drawers.draw_exemplar import DrawExemplar


class ExemplarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Основной layout виджета
        layout = QVBoxLayout(self)

        # Текстовое поле для информации об экземпляре
        self.info_text_edit = QTextEdit()
        self.info_text_edit.setMaximumHeight(100)
        self.info_text_edit.setReadOnly(True)
        layout.addWidget(QLabel("Информация об экземпляре:"))
        layout.addWidget(self.info_text_edit)

        # Канвас для визуализации
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Хранилище для объекта Exemplar и Drawer
        self.exemplar_obj = None
        self.draw_exemplar = None

    def reset_data(self, exemplar: Exemplar, color: str = 'green'):
        """Заполняет канвас на основе Exemplar и выводит информацию о точках."""
        self.exemplar_obj = exemplar

        # Обновляем текстовое поле с информацией
        self.info_text_edit.clear()

        # Информация о количестве точек
        points_count = len(exemplar)
        self.info_text_edit.append(f"Всего точек: {points_count}")

        # Информация о параметрах
        params = exemplar.get_param_names()
        if params:
            self.info_text_edit.append(f"Параметры: {', '.join(params)}")

        # Информация об оценке
        if exemplar.evaluation_result is not None:
            self.info_text_edit.append(f"Оценка: {exemplar.evaluation_result:.3f}")

        # Информация о точках
        if exemplar._points:
            self.info_text_edit.append("\nТочки:")
            sorted_points = sorted(exemplar._points.items(), key=lambda item: item[1][0])
            for point_name, (coord, track_id) in sorted_points:
                y = exemplar.signal.get_amplplitude_in_moment(coord)
                y_str = f"{y:.3f}" if y is not None else "вне сигнала"
                self.info_text_edit.append(f"  {point_name}: x={coord:.3f}с, y={y_str}мВ, track_id={track_id}")

        # Очищаем фигуру перед перерисовкой
        self.ax.clear()

        # Создаём визуализатор и получаем фигуру
        self.draw_exemplar = DrawExemplar(res_obj=exemplar, color=color)
        updated_fig = self.draw_exemplar.get_fig()

        # Заменяем текущую фигуру на обновлённую
        self.canvas.figure = updated_fig
        self.canvas.draw()


if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Визуализация Exemplar с точками")
            self.setGeometry(100, 100, 900, 700)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Создание тестового сигнала (синусоида с затуханием)
            time = [i * 0.01 for i in range(300)]
            signal_mv = [sin(t * 10) * (1 - t / 5) for t in time]
            test_signal = Signal(signal_mv=signal_mv, frequency=100)

            # Создание экземпляра Exemplar
            exemplar = Exemplar(signal=test_signal)

            # Добавление точек
            exemplar.add_point("P", 0.15, 101)
            exemplar.add_point("Q", 0.22, 101)
            exemplar.add_point("R", 0.30, 102)
            exemplar.add_point("S", 0.38, 102)
            exemplar.add_point("T", 0.55, 103)

            # Добавление параметров
            exemplar.add_parameter("heart_rate", 72.5)
            exemplar.add_parameter("qt_interval", 0.38)

            # Установка оценки
            exemplar.evaluation_result = 0.85

            # Создание виджета ExemplarWidget
            self.exemplar_widget = ExemplarWidget()

            # Заполняем виджет данными
            self.exemplar_widget.reset_data(exemplar, color='blue')

            # Добавляем виджет в layout
            layout.addWidget(self.exemplar_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()

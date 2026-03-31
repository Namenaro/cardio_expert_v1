import sys
from math import sin

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.run import Exemplar
from CORE.visual_debug.results_drawers.draw_exemplar import DrawExemplar


class ExemplarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exemplar = None
        self.draw_exemplar = None
        self.figure = None
        self.ax = None
        self.canvas = None
        self.init_ui()

    def init_ui(self):
        # Основной layout
        layout = QVBoxLayout(self)

        # Текстовое поле для ID
        self.id_label = QLabel()
        self.id_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: #f0f0f0;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.id_label)

        # Создаем фигуру и канвас
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def clear(self):
        """Очищает график перед загрузкой новых данных"""
        if self.ax:
            self.ax.clear()
        # Обнуляем ссылку на старый drawer, чтобы он мог быть собран GC
        self.draw_exemplar = None

    def reset_data(self, exemplar: Exemplar, color: str = 'green'):
        """Отображает экземпляр датасета"""
        self.exemplar = exemplar

        # Обновляем ID
        self.id_label.setText(f"ID экземпляра: {exemplar.id}")

        # Создаём визуализатор и получаем фигуру
        self.draw_exemplar = DrawExemplar(res_obj=exemplar, color=color)
        updated_fig = self.draw_exemplar.get_fig()

        # Заменяем текущую фигуру на обновлённую
        old_figure = self.canvas.figure
        self.canvas.figure = updated_fig

        # Закрываем старую фигуру, чтобы освободить память
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
        self.draw_exemplar = None
        self.exemplar = None


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

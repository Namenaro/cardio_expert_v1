import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QLabel, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug.results_drawers.draw_exemplars_pool import DrawExemplarsPool
from DA3.simulation_app.simulation_widgets.utils import (
    ExemplarColorManager,
    ExemplarInfoFormatter,
    TextEditHelper
)


# DA3/simulation_app/simulation_widgets/form_res_widget.py


class FormResWidget(QWidget):
    """Виджет для отображения сигнала и экземпляров из пула с кликабельным графиком."""

    def __init__(self, parent=None, padding_percent: float = 20):
        super().__init__(parent)
        self.padding_percent = padding_percent

        # Утилиты
        self.color_manager = ExemplarColorManager()
        self.formatter = ExemplarInfoFormatter()

        # Хранилища
        self.pool = None
        self.ground_truth = None
        self.draw_exemplars_pool = None

        # Фигура и канвас
        self.figure = None
        self.ax = None
        self.canvas = None

        # Текстовое поле
        self.exemplars_text = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Заголовок
        title_label = QLabel("Результаты симуляции формы")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: #f0f0f0;
                border-radius: 3px;
            }
        """)
        layout.addWidget(title_label)

        # Канвас
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Текстовое поле для списка экземпляров
        self.exemplars_text = QTextEdit()
        TextEditHelper.setup_text_edit(self.exemplars_text)
        layout.addWidget(QLabel("Созданные экземпляры:"))
        layout.addWidget(self.exemplars_text)

    def clear(self):
        """Очищает график и данные"""
        if self.ax:
            self.ax.clear()

        self.color_manager.clear()
        TextEditHelper.clear(self.exemplars_text)

        self.draw_exemplars_pool = None
        self.pool = None
        self.ground_truth = None

    def reset_data(self, pool: ExemplarsPool, ground_truth=None):
        """Заполняет виджет данными из пула экземпляров"""
        self.pool = pool
        self.ground_truth = ground_truth
        self.color_manager.clear()

        # Получаем экземпляры
        exemplars = pool.exemplars_sorted if pool.exemplars_sorted else []

        # Обновляем текстовое поле
        html = self.formatter.format_exemplars_list(exemplars, self.color_manager)
        TextEditHelper.set_html(self.exemplars_text, html)

        # Создаем визуализатор
        colors_list = self.color_manager.get_colors_list(exemplars)
        self.draw_exemplars_pool = DrawExemplarsPool(
            pool=pool,
            exemplar_colors=colors_list,
            padding_percent=self.padding_percent,
            show_legend=True
        )

        if ground_truth is not None:
            self.draw_exemplars_pool.set_ground_truth(ground_truth)

        # Обновляем канвас
        old_figure = self.canvas.figure
        self.canvas.figure = self.draw_exemplars_pool.get_fig()
        if old_figure is not None and old_figure != self.canvas.figure:
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
        self.draw_exemplars_pool = None
        self.pool = None
        self.ground_truth = None
        self.color_manager.clear()


if __name__ == "__main__":
    import sys
    import numpy as np
    from math import sin
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

    from CORE.signal_1d import Signal
    from CORE.run import Exemplar
    from CORE.run.exemplars_pool import ExemplarsPool



    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Визуализация ExemplarsPool")
            self.setGeometry(100, 100, 1000, 700)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Главный layout
            main_layout = QVBoxLayout(central_widget)

            # Создаем виджет FormResWidget с padding 30%
            self.form_widget = FormResWidget(padding_percent=30)
            main_layout.addWidget(self.form_widget)

            # Создаем тестовый пул с тремя экземплярами и ground truth
            pool, ground_truth = self._create_pool_with_ground_truth()

            # Передаем пул и ground truth в виджет
            self.form_widget.reset_data(pool, ground_truth)

        def _create_test_signal(self):
            """Создает тестовый сигнал (синусоида с затуханием)."""
            time = [i * 0.01 for i in range(100)]
            signal_mv = [sin(t * 10) * (1 - t / 5) for t in time]
            return Signal(signal_mv=signal_mv, frequency=100)

        def _create_exemplar(self, signal: Signal, points: dict, evaluation: float, track_id_base: int = 100):
            """Создает экземпляр Exemplar с заданными точками и оценкой."""
            exemplar = Exemplar(signal=signal)

            for i, (point_name, x_coord) in enumerate(points.items()):
                exemplar.add_point(point_name, x_coord, track_id_base + i)

            exemplar.add_parameter("heart_rate", 70.0 + np.random.random() * 10)
            exemplar.add_parameter("qt_interval", 0.35 + np.random.random() * 0.1)

            if evaluation is not None:
                exemplar.evaluation_result = evaluation

            return exemplar

        def _create_pool_with_ground_truth(self):
            """Создает пул с тремя экземплярами и ground truth."""
            signal = self._create_test_signal()
            pool = ExemplarsPool(signal=signal, max_size=None)

            # Ground Truth (черный)
            ground_truth_points = {
                "P": 0.15, "Q": 0.22, "R": 0.30, "S": 0.38, "T": 0.55
            }
            ground_truth = self._create_exemplar(signal, ground_truth_points, evaluation=1.0, track_id_base=50)

            # Экземпляр 1 (хороший) - зеленый
            points1 = {
                "P": 0.16, "Q": 0.23, "R": 0.31, "S": 0.39, "T": 0.54
            }
            exemplar1 = self._create_exemplar(signal, points1, evaluation=0.95, track_id_base=100)
            pool.add_exemplar(exemplar1)

            # Экземпляр 2 (средний) - желто-зеленый
            points2 = {
                "P": 0.17, "Q": 0.24, "R": 0.32, "S": 0.40, "T": 0.53
            }
            exemplar2 = self._create_exemplar(signal, points2, evaluation=0.65, track_id_base=200)
            pool.add_exemplar(exemplar2)

            # Экземпляр 3 (плохой) - красный
            points3 = {
                "P": 0.14, "Q": 0.21, "R": 0.29, "S": 0.37, "T": 0.56
            }
            exemplar3 = self._create_exemplar(signal, points3, evaluation=0.25, track_id_base=300)
            pool.add_exemplar(exemplar3)

            return pool, ground_truth


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()
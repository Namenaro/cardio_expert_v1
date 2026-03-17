from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from typing import Optional

from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug.results_drawers.draw_exemplars_pool import DrawExemplarsPool


class FormResWidget(QWidget):
    """Виджет для отображения сигнала и экземпляров из пула с кликабельным графиком."""

    def __init__(self, parent=None, padding_percent: float = 20):
        """
        Args:
            parent: родительский виджет
            padding_percent: процент от длины интервала между крайними точками для отступов
        """
        super().__init__(parent)

        self.padding_percent = padding_percent
        self.current_pool: Optional[ExemplarsPool] = None
        self.current_ground_truth: Optional[Exemplar] = None
        self.draw_exemplars_pool: Optional[DrawExemplarsPool] = None

        self.init_ui()

    def init_ui(self):
        """Инициализирует пользовательский интерфейс."""
        # Основной layout
        layout = QVBoxLayout(self)

        # Текстовое поле для информации о лучшем экземпляре
        self.info_label = QLabel("Информация о пуле:")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.info_label)

        # Текстовое поле для подробной информации
        self.info_text_edit = QTextEdit()
        self.info_text_edit.setMaximumHeight(150)
        self.info_text_edit.setReadOnly(True)
        layout.addWidget(self.info_text_edit)

        # Канвас для визуализации
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def _update_info_text(self):
        """Обновляет текстовое поле с информацией о пуле."""
        if not self.current_pool:
            self.info_text_edit.clear()
            self.info_label.setText("Информация о пуле:")
            return

        self.info_text_edit.clear()

        # Общая информация
        self.info_text_edit.append(f"Всего экземпляров в пуле: {self.current_pool.size}")

        if self.current_ground_truth:
            self.info_text_edit.append("Ground Truth: присутствует")

        # Информация о лучшем экземпляре
        if self.current_pool.exemplars_sorted:
            best = self.current_pool.exemplars_sorted[0]
            self.info_text_edit.append("\n=== Лучший экземпляр ===")

            if best.evaluation_result is not None:
                self.info_text_edit.append(f"Оценка: {best.evaluation_result:.3f}")
                color = self._get_color_from_score(best.evaluation_result)
                self.info_label.setText(f"Лучшая оценка: {best.evaluation_result:.3f}")
                self.info_label.setStyleSheet(
                    f"font-size: 14px; font-weight: bold; padding: 5px; color: {color};"
                )
            else:
                self.info_label.setText("Лучшая оценка: —")
                self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")

            # Точки лучшего экземпляра
            self.info_text_edit.append("Точки:")
            sorted_points = sorted(best._points.items(), key=lambda item: item[1][0])
            for point_name, (coord, track_id) in sorted_points:
                y = best.get_signal().get_amplplitude_in_moment(coord)
                y_str = f"{y:.3f}" if y is not None else "вне сигнала"
                self.info_text_edit.append(f"  {point_name}: x={coord:.3f}с, y={y_str}мВ")

            # Параметры лучшего экземпляра
            params = best.get_param_names()
            if params:
                self.info_text_edit.append("Параметры:")
                for param in params:
                    value = best.get_parameter_value(param)
                    self.info_text_edit.append(f"  {param}: {value}")

    def _get_color_from_score(self, score: Optional[float]) -> str:
        """Возвращает цвет на основе оценки."""
        if score is None:
            return '#808080'

        import numpy as np
        normalized = np.clip(score, 0, 1)
        red = int(255 * (1 - normalized))
        green = int(255 * normalized)
        blue = 0
        return f'#{red:02x}{green:02x}{blue:02x}'

    def reset_data(self, pool: ExemplarsPool, ground_truth: Optional[Exemplar] = None):
        """
        Сбрасывает данные и отрисовывает новый пул экземпляров.

        Args:
            pool: Объект ExemplarsPool с сигналом и экземплярами
            ground_truth: Эталонный экземпляр (рисуется черным), если есть
        """
        self.current_pool = pool
        self.current_ground_truth = ground_truth

        # Создаем визуализатор
        self.draw_exemplars_pool = DrawExemplarsPool(
            pool=pool,
            padding_percent=self.padding_percent
        )

        # Устанавливаем ground truth
        self.draw_exemplars_pool.set_ground_truth(ground_truth)

        # Получаем фигуру
        updated_fig = self.draw_exemplars_pool.get_fig()

        # Заменяем текущую фигуру на обновлённую
        self.canvas.figure = updated_fig

        # Обновляем информацию
        self._update_info_text()

        # Перерисовываем канвас
        self.canvas.draw()

    def clear(self):
        """Очищает виджет."""
        self.current_pool = None
        self.current_ground_truth = None
        self.draw_exemplars_pool = None

        self.figure.clear()
        self.canvas.draw()

        self.info_label.setText("Информация о пуле:")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        self.info_text_edit.clear()


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
import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from typing import Optional, List, Tuple

from CORE.signal_1d import Signal
from CORE.run import Exemplar
from CORE.visual_debug.plt_visualisation import Drawer, LineStyle
from CORE.run.exemplars_pool import ExemplarsPool


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

        # Создаем layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Создаем текстовое поле для оценки лучшего экземпляра
        self.best_score_label = QLabel("Лучшая оценка: —")
        self.best_score_label.setAlignment(Qt.AlignCenter)
        self.best_score_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(self.best_score_label)

        # Создаем фигуру для matplotlib
        self.figure, self.ax = plt.subplots(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Создаем Drawer для кликабельности
        self.drawer = Drawer(self.ax)

        # Сохраняем текущий пул
        self.current_pool: Optional[ExemplarsPool] = None

    def _get_color_from_score(self, score: Optional[float]) -> str:
        """Возвращает цвет на основе оценки."""
        if score is None:
            return '#808080'  # Серый для None

        normalized = np.clip(score, 0, 1)
        red = int(255 * (1 - normalized))
        green = int(255 * normalized)
        blue = 0
        return f'#{red:02x}{green:02x}{blue:02x}'

    def _get_all_points_from_pool(self, pool: ExemplarsPool, ground_truth: Optional[Exemplar] = None) -> List[
        Tuple[float, float, str, Optional[Exemplar]]]:
        """
        Собирает все точки из всех экземпляров пула и ground_truth.

        Returns:
            List of tuples (x, y, point_name, exemplar)
        """
        all_points = []

        # Точки из пула
        for exemplar in pool.exemplars_sorted:
            signal = exemplar.get_signal()
            for point_name in exemplar._points.keys():
                x = exemplar.get_point_coord(point_name)
                if x is not None:
                    y = signal.get_amplplitude_in_moment(x)
                    if y is not None:
                        all_points.append((x, y, point_name, exemplar))

        # Точки из ground_truth
        if ground_truth is not None:
            signal = ground_truth.get_signal()
            for point_name in ground_truth._points.keys():
                x = ground_truth.get_point_coord(point_name)
                if x is not None:
                    y = signal.get_amplplitude_in_moment(x)
                    if y is not None:
                        all_points.append((x, y, point_name, ground_truth))

        return all_points

    def _calculate_x_limits(self, pool: ExemplarsPool, ground_truth: Optional[Exemplar] = None) -> Tuple[float, float]:
        """
        Рассчитывает границы отображения по оси X с учетом паддинга.

        Returns:
            Tuple (x_min, x_max) - границы для отображения
        """
        all_points = self._get_all_points_from_pool(pool, ground_truth)

        if not all_points:
            # Если нет точек, показываем весь сигнал
            signal = pool.signal
            return signal.time[0], signal.time[-1]

        # Находим самую левую и самую правую точки
        x_coords = [p[0] for p in all_points]
        x_min = min(x_coords)
        x_max = max(x_coords)

        # Рассчитываем паддинг
        interval_length = x_max - x_min
        padding = interval_length * (self.padding_percent / 100)

        # Добавляем паддинг слева и справа
        x_min_padded = x_min - padding
        x_max_padded = x_max + padding

        # Проверяем, не выходим ли за пределы сигнала
        signal = pool.signal
        x_min_padded = max(x_min_padded, signal.time[0])
        x_max_padded = min(x_max_padded, signal.time[-1])

        return x_min_padded, x_max_padded

    def _add_exemplar_to_drawer(self, exemplar: Exemplar, color: str, label: str, is_ground_truth: bool = False):
        """Добавляет экземпляр в drawer для отрисовки."""
        # Получаем точки экземпляра
        points = []
        signal = exemplar.get_signal()

        for point_name in exemplar._points.keys():
            x = exemplar.get_point_coord(point_name)
            if x is not None:
                y = signal.get_amplplitude_in_moment(x)
                if y is not None:
                    points.append((x, y, point_name))

        # Сортируем точки по x
        if points:
            points.sort(key=lambda p: p[0])

            # Рисуем ломаную линию через все точки
            for i in range(len(points) - 1):
                self.drawer.add_segment(
                    x1=points[i][0], y1=points[i][1],
                    x2=points[i + 1][0], y2=points[i + 1][1],
                    color=color, style=LineStyle.SOLID,
                    label=label if i == 0 else None,  # Метка только для первого сегмента
                    zorder=4 if is_ground_truth else 3  # Ground truth выше обычных экземпляров
                )

            # Добавляем точки маркерами

            for x, y, point_name in points:
                self.drawer.add_point(
                    x=x, y=y,
                    color=color,
                    label=point_name,
                    show_label_near_point=True,
                    zorder=5 if is_ground_truth else 4
                )

    def reset_data(self, pool: ExemplarsPool, ground_truth: Optional[Exemplar] = None):
        """
        Сбрасывает данные и отрисовывает новый пул экземпляров.

        Args:
            pool: Объект ExemplarsPool с сигналом и экземплярами
            ground_truth: Эталонный экземпляр (рисуется черным), если есть
        """
        self.current_pool = pool

        # Очищаем drawer
        self.drawer.renderer.signals.clear()
        self.drawer.renderer.vertical_lines.clear()
        self.drawer.renderer.vertical_line_groups.clear()
        self.drawer.renderer.intervals.clear()
        self.drawer.renderer.points.clear()
        self.drawer.renderer.segments.clear()

        # Добавляем сигнал из пула
        self.drawer.add_signal(pool.signal, color='blue', name='Сигнал ЭКГ')

        # Добавляем ground truth если есть (черным цветом)
        if ground_truth is not None:
            self._add_exemplar_to_drawer(
                exemplar=ground_truth,
                color='#000000',  # Черный
                label='Ground Truth',
                is_ground_truth=True
            )

        # Добавляем все экземпляры из пула
        if pool.exemplars_sorted:
            for i, exemplar in enumerate(pool.exemplars_sorted):
                color = self._get_color_from_score(exemplar.evaluation_result)

                if exemplar.evaluation_result is not None:
                    label = f'Экземпляр {i + 1} (оценка: {exemplar.evaluation_result:.2f})'
                else:
                    label = f'Экземпляр {i + 1} (без оценки)'

                self._add_exemplar_to_drawer(exemplar, color, label)

            # Обновляем текстовое поле с оценкой лучшего экземпляра
            best_exemplar = pool.exemplars_sorted[0]
            best_score = best_exemplar.evaluation_result
            if best_score is not None:
                self.best_score_label.setText(f"Лучшая оценка: {best_score:.3f}")
                color = self._get_color_from_score(best_score)
                self.best_score_label.setStyleSheet(
                    f"font-size: 14px; font-weight: bold; padding: 5px; color: {color};"
                )
            else:
                self.best_score_label.setText("Лучшая оценка: —")
                self.best_score_label.setStyleSheet(
                    "font-size: 14px; font-weight: bold; padding: 5px;"
                )
        else:
            self.best_score_label.setText("Нет экземпляров")

        # Перерисовываем
        self.drawer.redraw()

        # Устанавливаем границы по X с учетом паддинга
        x_min, x_max = self._calculate_x_limits(pool, ground_truth)
        self.ax.set_xlim(x_min, x_max)

        self.canvas.draw()

    def clear(self):
        """Очищает виджет."""
        self.current_pool = None
        self.drawer.renderer.signals.clear()
        self.drawer.renderer.vertical_lines.clear()
        self.drawer.renderer.vertical_line_groups.clear()
        self.drawer.renderer.intervals.clear()
        self.drawer.renderer.points.clear()
        self.drawer.renderer.segments.clear()
        self.drawer.redraw()
        self.canvas.draw()
        self.best_score_label.setText("Лучшая оценка: —")
        self.best_score_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")


if __name__ == "__main__":
    import sys
    import numpy as np
    from math import sin
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

    from CORE.signal_1d import Signal
    from CORE.run import Exemplar


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

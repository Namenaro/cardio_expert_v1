from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from typing import Optional

from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug.results_drawers.draw_exemplars_pool import DrawExemplarsPool


class ExemplarCard(QWidget):
    """Виджет-карточка для отображения одного экземпляра с ground truth."""

    def __init__(self, exemplar: Exemplar, ground_truth: Exemplar, pool_signal,
                 padding_percent: float = 20, min_height_mm: float = 40, parent=None):
        """
        Args:
            exemplar: экземпляр для отображения
            ground_truth: эталонный экземпляр (рисуется черным)
            pool_signal: сигнал пула (общий для всех)
            padding_percent: отступ в процентах
            min_height_mm: минимальная высота карточки в миллиметрах
            parent: родительский виджет
        """
        super().__init__(parent)

        # Создаем layout для карточки
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        # Создаем временный пул с одним экземпляром
        temp_pool = ExemplarsPool(signal=pool_signal, max_size=None)
        temp_pool.add_exemplar(exemplar)

        # Создаем рисовалку БЕЗ ЛЕГЕНДЫ (show_legend=False)
        self.drawer = DrawExemplarsPool(
            pool=temp_pool,
            padding_percent=padding_percent,
            show_legend=False
        )
        self.drawer.set_ground_truth(ground_truth)

        # Получаем фигуру
        self.fig = self.drawer.get_fig()

        # Создаем канвас
        self.canvas = FigureCanvas(self.fig)

        # Настраиваем политику размера для канваса
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setMinimumHeight(int(min_height_mm * 3.78))  # Конвертация мм в пиксели (примерно)

        layout.addWidget(self.canvas)

        # Сохраняем экземпляр для информации (опционально)
        self.exemplar = exemplar


class FormResWidgetExtended(QWidget):
    """Виджет для отображения всех экземпляров пула по отдельности с прокруткой."""

    def __init__(self, parent=None, padding_percent: float = 20, min_card_height_mm: float = 40):
        """
        Args:
            parent: родительский виджет
            padding_percent: процент отступа для каждого графика
            min_card_height_mm: минимальная высота каждой карточки в миллиметрах
        """
        super().__init__(parent)

        self.padding_percent = padding_percent
        self.min_card_height_mm = min_card_height_mm
        self.current_pool: Optional[ExemplarsPool] = None
        self.current_ground_truth: Optional[Exemplar] = None

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Создаем область прокрутки
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(self.scroll_area)

        # Создаем виджет-контейнер для карточек
        self.container_widget = QWidget()
        self.container_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setWidget(self.container_widget)

        # Layout для карточек (вертикальный)
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.container_widget.setLayout(self.cards_layout)

        # Список карточек для возможного обновления
        self.cards: list[ExemplarCard] = []

    def resizeEvent(self, event):
        """Обработчик изменения размера виджета."""
        super().resizeEvent(event)
        # При изменении размера обновляем размеры карточек
        if self.cards:
            # Вычисляем оптимальную высоту для каждой карточки
            available_height = self.scroll_area.viewport().height()
            card_count = len(self.cards)

            if card_count > 0:
                # Вычитаем отступы между карточками
                spacing_total = (card_count - 1) * 10
                margins_total = 20  # Отступы контейнера

                # Доступная высота для всех карточек
                height_for_cards = available_height - spacing_total - margins_total

                # Высота одной карточки
                card_height = max(
                    int(self.min_card_height_mm * 3.78),  # Минимум в пикселях
                    height_for_cards // card_count  # Адаптивная высота
                )

                # Устанавливаем минимальную высоту для каждой карточки
                for card in self.cards:
                    card.canvas.setMinimumHeight(card_height)
                    card.canvas.updateGeometry()

    def reset_data(self, pool: ExemplarsPool, ground_truth: Optional[Exemplar] = None):
        """
        Сбрасывает данные и создает карточки для каждого экземпляра.

        Args:
            pool: Объект ExemplarsPool с сигналом и экземплярами
            ground_truth: Эталонный экземпляр (обязателен для отображения на каждой карточке)
        """
        self.current_pool = pool
        self.current_ground_truth = ground_truth

        # Очищаем старые карточки
        self._clear_cards()

        # Если нет ground_truth, нечего показывать
        if ground_truth is None:
            return

        # Создаем карточку для каждого экземпляра в пуле
        for exemplar in pool.exemplars_sorted:
            card = ExemplarCard(
                exemplar=exemplar,
                ground_truth=ground_truth,
                pool_signal=pool.signal,
                padding_percent=self.padding_percent,
                min_height_mm=self.min_card_height_mm
            )
            self.cards_layout.addWidget(card)
            self.cards.append(card)

        # Добавляем растяжку в конце, чтобы карточки не растягивались
        self.cards_layout.addStretch()

        # Вызываем resizeEvent для расчета размеров
        self.resizeEvent(None)

    def _clear_cards(self):
        """Очищает все карточки."""
        for card in self.cards:
            card.deleteLater()
        self.cards.clear()

        # Очищаем layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def clear(self):
        """Очищает виджет."""
        self.current_pool = None
        self.current_ground_truth = None
        self._clear_cards()


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
            self.setWindowTitle("Визуализация ExemplarsPool (по экземплярам)")
            self.setGeometry(100, 100, 800, 900)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Главный layout
            main_layout = QVBoxLayout(central_widget)

            # Создаем виджет FormResWidgetExtended с минимальной высотой карточки 40 мм
            self.form_widget = FormResWidgetExtended(
                padding_percent=20,
                min_card_height_mm=40  # 40 мм минимальная высота каждой карточки
            )
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

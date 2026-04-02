from typing import Optional, List

import matplotlib.pyplot as plt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QWidget, QScrollArea, QSizePolicy, QLabel, QTextEdit, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug.results_drawers.draw_exemplars_pool import DrawExemplarsPool
from DA3.simulation_app.simulation_widgets.utils import (
    ExemplarColorManager,
    ExemplarInfoFormatter,
    TextEditHelper
)


# DA3/simulation_app/simulation_widgets/form_res_widget_extended.py


class ExemplarCard(QWidget):
    """Виджет-карточка для отображения одного экземпляра с ground truth и текстовой информацией справа."""

    def __init__(self, exemplar: Exemplar, ground_truth: Exemplar, pool_signal,
                 padding_percent: float = 20, min_height_mm: float = 40,
                 color: str = '#808080', index: int = 0, rank: int = 0, parent=None):
        """
        Args:
            exemplar: экземпляр для отображения
            ground_truth: эталонный экземпляр (рисуется черным)
            pool_signal: сигнал пула (общий для всех)
            padding_percent: отступ в процентах
            min_height_mm: минимальная высота карточки в миллиметрах
            color: цвет экземпляра
            index: индекс экземпляра
            rank: место в рейтинге (1 - лучший)
            parent: родительский виджет
        """
        super().__init__(parent)

        self.exemplar = exemplar
        self.color = color
        self.index = index
        self.rank = rank
        self.formatter = ExemplarInfoFormatter()

        # Основной layout карточки (горизонтальный)
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Левая часть - график
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок с местом
        rank_text = f"#{rank}" if rank > 0 else "Без оценки"
        rank_label = QLabel(rank_text)
        rank_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                font-size: 12px;
                padding: 2px 5px;
                background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1);
                border-radius: 10px;
            }}
        """)
        rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_label.setMaximumWidth(50)
        left_layout.addWidget(rank_label)

        # Создаем временный пул с одним экземпляром
        temp_pool = ExemplarsPool(signal=pool_signal, max_size=None)
        temp_pool.add_exemplar(exemplar)

        # Создаем рисовалку БЕЗ ЛЕГЕНДЫ
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
        self.canvas.setMinimumHeight(int(min_height_mm * 3.78))
        self.canvas.setMinimumWidth(600)

        left_layout.addWidget(self.canvas)
        layout.addWidget(left_widget, 3)  # График занимает 3/4 ширины

        # Правая часть - текстовое поле с информацией
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок с оценкой
        if exemplar.evaluation_result is not None:
            score_label = QLabel(f"Оценка: {exemplar.evaluation_result:.3f}")
            score_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    font-size: 12px;
                    padding: 4px;
                    background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1);
                    border-radius: 4px;
                }}
            """)
            score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            right_layout.addWidget(score_label)

        # Текстовое поле для информации
        self.info_text = QTextEdit()
        TextEditHelper.setup_text_edit(self.info_text, max_height=200)
        right_layout.addWidget(self.info_text)

        layout.addWidget(right_widget, 1)  # Текст занимает 1/4 ширины

        # Обновляем текстовую информацию
        self._update_info()

    def _update_info(self):
        """Обновляет текстовую информацию об экземпляре."""
        # Форматируем информацию с помощью существующего форматтера
        html = self.formatter.format_exemplar(self.exemplar, self.index, self.color)
        TextEditHelper.set_html(self.info_text, html)

    def cleanup(self):
        """Очищает ресурсы matplotlib"""
        if self.canvas:
            self.canvas.deleteLater()
        if self.fig:
            plt.close(self.fig)
        self.fig = None
        self.canvas = None
        self.drawer = None
        self.info_text = None


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

        # Утилиты
        self.color_manager = ExemplarColorManager()

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # Верхняя панель с лучшей оценкой
        self.best_score_label = QLabel()
        self.best_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.best_score_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e9;
                border: 1px solid #4caf50;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #2e7d32;
            }
        """)
        main_layout.addWidget(self.best_score_label)

        # Создаем область прокрутки
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(self.scroll_area)

        # Создаем виджет-контейнер для карточек
        self.container_widget = QWidget()
        self.container_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_area.setWidget(self.container_widget)

        # Layout для карточек (вертикальный)
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)
        self.container_widget.setLayout(self.cards_layout)

        # Список карточек
        self.cards: List[ExemplarCard] = []

    def _get_sorted_exemplars(self, exemplars: List[Exemplar]) -> List[Exemplar]:
        """Сортирует экземпляры от лучшего к худшему по оценке."""
        # Сортировка: None идут в конец, остальные по убыванию оценки
        return sorted(
            exemplars,
            key=lambda e: (e.evaluation_result is None, -e.evaluation_result if e.evaluation_result is not None else 0)
        )

    def _update_best_score(self, exemplars: List[Exemplar]):
        """Обновляет отображение лучшей оценки."""
        # Находим максимальную оценку среди экземпляров
        valid_scores = [e.evaluation_result for e in exemplars if e.evaluation_result is not None]

        if valid_scores:
            best_score = max(valid_scores)
            self.best_score_label.setText(f"🏆 Лучшая оценка в пуле: {best_score:.3f} 🏆")
            self.best_score_label.show()
        else:
            self.best_score_label.setText("📊 Оценки экземпляров отсутствуют")
            self.best_score_label.show()

    def resizeEvent(self, event):
        """Обработчик изменения размера виджета."""
        super().resizeEvent(event)
        if self.cards:
            available_height = self.scroll_area.viewport().height()
            card_count = len(self.cards)

            if card_count > 0:
                # Вычитаем отступы между карточками
                spacing_total = (card_count - 1) * 15
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

    def _create_card(self, exemplar: Exemplar, ground_truth: Exemplar, pool_signal,
                     color: str, index: int, rank: int) -> ExemplarCard:
        """Создает карточку для экземпляра."""
        return ExemplarCard(
            exemplar=exemplar,
            ground_truth=ground_truth,
            pool_signal=pool_signal,
            padding_percent=self.padding_percent,
            min_height_mm=self.min_card_height_mm,
            color=color,
            index=index,
            rank=rank
        )

    def _clear_cards(self):
        """Очищает все карточки."""
        for card in self.cards:
            card.cleanup()
            card.deleteLater()
        self.cards.clear()

        # Очищаем layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def reset_data(self, pool: ExemplarsPool, ground_truth: Optional[Exemplar] = None):
        """
        Сбрасывает данные и создает карточки для каждого экземпляра.
        Экземпляры сортируются от лучшего к худшему.

        Args:
            pool: Объект ExemplarsPool с сигналом и экземплярами
            ground_truth: Эталонный экземпляр (обязателен для отображения на каждой карточке)
        """
        self.current_pool = pool
        self.current_ground_truth = ground_truth
        self.color_manager.clear()

        # Очищаем старые карточки
        self._clear_cards()

        # Если нет ground_truth, нечего показывать
        if ground_truth is None:
            self.best_score_label.hide()
            self._show_no_ground_truth_message()
            return

        # Получаем и сортируем экземпляры от лучшего к худшему
        exemplars = pool.exemplars_sorted if pool.exemplars_sorted else []
        sorted_exemplars = self._get_sorted_exemplars(exemplars)

        # Обновляем отображение лучшей оценки
        self._update_best_score(sorted_exemplars)

        # Создаем карточку для каждого экземпляра
        for rank, exemplar in enumerate(sorted_exemplars, start=1):
            # Цвет на основе индекса (используем исходный индекс для согласованности)
            original_index = exemplars.index(exemplar) if exemplar in exemplars else rank - 1
            color = self.color_manager.get_color(exemplar, original_index)

            card = self._create_card(
                exemplar=exemplar,
                ground_truth=ground_truth,
                pool_signal=pool.signal,
                color=color,
                index=original_index,
                rank=rank if exemplar.evaluation_result is not None else 0
            )
            self.cards_layout.addWidget(card)
            self.cards.append(card)

        # Добавляем растяжку в конце
        self.cards_layout.addStretch()

        # Вызываем resizeEvent для расчета размеров
        self.resizeEvent(None)

    def _show_no_ground_truth_message(self):
        """Показывает сообщение об отсутствии ground truth."""
        message_label = QLabel("Нет эталонного экземпляра (ground truth) для отображения")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                font-style: italic;
                padding: 20px;
            }
        """)
        self.cards_layout.addWidget(message_label)

    def clear(self):
        """Очищает виджет."""
        self.current_pool = None
        self.current_ground_truth = None
        self.color_manager.clear()
        self.best_score_label.hide()
        self._clear_cards()

    def cleanup(self):
        """Очищает все ресурсы."""
        self._clear_cards()
        self.color_manager.clear()
        if self.scroll_area:
            self.scroll_area.deleteLater()

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

import sys
from math import sin

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.visual_debug import StepRes
from CORE.visual_debug import TrackRes, PS_Res
from CORE.visual_debug.results_drawers.draw_exemplars_pool import DrawExemplarsPool
from CORE.visual_debug.results_drawers.draw_step_res import DrawStepRes
from DA3.simulation_app.simulation_widgets.utils import (
    ExemplarColorManager,
    ExemplarInfoFormatter,
    XLimitsCalculator,
    TextEditHelper
)


class StepResWidget(QWidget):
    """
    Виджет для отображения полной информации о шаге:
    - Верхняя часть: отображение треков шага (DrawStepRes)
    - Средняя часть: отображение созданных экземпляров (DrawExemplarsPool)
    - Нижняя часть: текстовое поле со списком экземпляров
    """

    def __init__(self, parent=None, padding_percent: float = 20):
        super().__init__(parent)
        self.padding_percent = padding_percent

        # Утилиты
        self.color_manager = ExemplarColorManager()
        self.formatter = ExemplarInfoFormatter()
        self.limits_calculator = XLimitsCalculator(padding_percent)

        # Хранилища
        self.step_res_obj = None
        self.draw_step_res = None
        self.draw_exemplars_pool = None

        # Фигуры и канвасы
        self.figure_step = None
        self.ax_step = None
        self.canvas_step = None

        self.figure_exemplars = None
        self.ax_exemplars = None
        self.canvas_exemplars = None

        # Текстовое поле
        self.exemplars_text = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ID шага
        self.id_text_edit = QTextEdit()
        self.id_text_edit.setMaximumHeight(50)
        self.id_text_edit.setReadOnly(True)
        layout.addWidget(QLabel("ID шага (StepRes):"))
        layout.addWidget(self.id_text_edit)

        # Канвас с треками
        self.figure_step, self.ax_step = plt.subplots(figsize=(10, 4))
        self.canvas_step = FigureCanvas(self.figure_step)
        layout.addWidget(self.canvas_step)

        # Канвас с экземплярами
        self.figure_exemplars, self.ax_exemplars = plt.subplots(figsize=(10, 4))
        self.canvas_exemplars = FigureCanvas(self.figure_exemplars)
        layout.addWidget(self.canvas_exemplars)

        # Текстовое поле для списка экземпляров
        self.exemplars_text = QTextEdit()
        TextEditHelper.setup_text_edit(self.exemplars_text)
        layout.addWidget(QLabel("Созданные экземпляры:"))
        layout.addWidget(self.exemplars_text)

    def clear(self):
        """Очищает все данные и графики"""
        if self.ax_step:
            self.ax_step.clear()
        if self.ax_exemplars:
            self.ax_exemplars.clear()

        self.color_manager.clear()
        TextEditHelper.clear(self.exemplars_text)

        self.draw_step_res = None
        self.draw_exemplars_pool = None
        self.step_res_obj = None

    def _update_canvas(self, canvas, new_figure):
        """Обновляет канвас новой фигурой"""
        old_figure = canvas.figure
        canvas.figure = new_figure
        if old_figure is not None and old_figure != new_figure:
            plt.close(old_figure)
        canvas.draw()

    def reset_data(self, step_res: StepRes):
        """Заполняет виджет данными из StepRes"""
        self.step_res_obj = step_res
        self.color_manager.clear()

        # Обновляем ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(step_res.id))

        # Получаем экземпляры
        exemplars = step_res.get_exemplars() or []

        # Обновляем текстовое поле
        html = self.formatter.format_exemplars_list(exemplars, self.color_manager)
        TextEditHelper.set_html(self.exemplars_text, html)

        # Рассчитываем объединенные границы
        combined_left, combined_right = self.limits_calculator.calculate_combined_limits(
            step_res, DrawStepRes, DrawExemplarsPool
        )

        # Рисуем треки
        color_map = self.color_manager.get_color_map(exemplars)
        self.draw_step_res = DrawStepRes(
            res_obj=step_res,
            exemplar_color_map=color_map,
            padding_percent=self.padding_percent,
            x_limits=(combined_left, combined_right)
        )
        self._update_canvas(self.canvas_step, self.draw_step_res.get_fig())

        # Рисуем экземпляры
        if exemplars:
            colors_list = self.color_manager.get_colors_list(exemplars)
            self.draw_exemplars_pool = DrawExemplarsPool(
                exemplars=exemplars,
                exemplar_colors=colors_list,
                padding_percent=self.padding_percent,
                show_legend=False,
                x_limits=(combined_left, combined_right)
            )
            self._update_canvas(self.canvas_exemplars, self.draw_exemplars_pool.get_fig())
        else:
            # Пустой график
            self.ax_exemplars.clear()
            self.ax_exemplars.set_xlim(combined_left, combined_right)
            self.ax_exemplars.text(0.5, 0.5, 'Нет созданных экземпляров',
                                   horizontalalignment='center',
                                   verticalalignment='center',
                                   transform=self.ax_exemplars.transAxes)
            self.canvas_exemplars.draw()

    def cleanup(self):
        """Очищает ресурсы matplotlib"""
        if self.canvas_step:
            self.canvas_step.deleteLater()
        if self.figure_step:
            plt.close(self.figure_step)

        if self.canvas_exemplars:
            self.canvas_exemplars.deleteLater()
        if self.figure_exemplars:
            plt.close(self.figure_exemplars)

        self.figure_step = None
        self.ax_step = None
        self.canvas_step = None
        self.figure_exemplars = None
        self.ax_exemplars = None
        self.canvas_exemplars = None
        self.draw_step_res = None
        self.draw_exemplars_pool = None
        self.step_res_obj = None
        self.color_manager.clear()

if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Визуализация StepRes с несколькими треками")
            self.setGeometry(100, 100, 800, 600)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Создание тестового сигнала
            initial_signal = Signal(signal_mv=[0.1 - sin(i) for i in range(80)], frequency=2)

            # Создаём PS объекты для первого трека
            ps_res_list_track1 = [
                PS_Res(
                    id=1,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[11.2, 12.5]  # две точки для первого PS первого трека
                ),
                PS_Res(
                    id=2,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[13.2, 14.5]  # две точки для второго PS первого трека
                )
            ]

            # Создаём PS объекты для второго трека
            ps_res_list_track2 = [
                PS_Res(
                    id=3,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[10.5, 11.8]  # две точки для первого PS второго трека
                ),
                PS_Res(
                    id=4,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[12.0, 13.8]  # две точки для второго PS второго трека
                )
            ]

            # Создаём треки
            track1 = TrackRes(
                id=101,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                ps_res_objs=ps_res_list_track1,
                sm_res_objs=[]  # пустой список для совместимости
            )

            track2 = TrackRes(
                id=102,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                ps_res_objs=ps_res_list_track2,
                sm_res_objs=[]  # пустой список для совместимости
            )

            # Создаём StepRes с двумя треками
            test_step_res = StepRes(
                id=42,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                tracks_results=[track1, track2]
            )

            # Создание виджета StepResWidget
            self.step_res_widget = StepResWidget()

            # Заполняем виджет данными из тестового StepRes
            self.step_res_widget.reset_data(test_step_res)

            # Добавляем виджет в layout
            layout.addWidget(self.step_res_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()

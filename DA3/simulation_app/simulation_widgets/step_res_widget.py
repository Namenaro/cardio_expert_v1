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


class StepResWidget(QWidget):
    """
    Виджет для отображения полной информации о шаге:
    - Верхняя часть: отображение треков шага (DrawStepRes)
    - Нижняя часть: отображение созданных экземпляров (DrawExemplarsPool)

    Цвета экземпляров синхронизированы между верхним и нижним канвасами.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
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

        # Словарь для хранения цветов экземпляров
        self.exemplar_colors = {}

        self.init_ui()

    def init_ui(self):
        # Основной layout виджета
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Текстовое поле для ID шага
        self.id_text_edit = QTextEdit()
        self.id_text_edit.setMaximumHeight(50)
        self.id_text_edit.setReadOnly(True)
        layout.addWidget(QLabel("ID шага (StepRes):"))
        layout.addWidget(self.id_text_edit)

        # Первый канвас - треки шага (верхняя часть)
        self.figure_step, self.ax_step = plt.subplots(figsize=(10, 4))
        self.canvas_step = FigureCanvas(self.figure_step)
        layout.addWidget(self.canvas_step)

        # Второй канвас - созданные экземпляры (нижняя часть)
        self.figure_exemplars, self.ax_exemplars = plt.subplots(figsize=(10, 4))
        self.canvas_exemplars = FigureCanvas(self.figure_exemplars)
        layout.addWidget(self.canvas_exemplars)

    def _generate_color_from_index(self, index: int) -> str:
        """
        Генерирует цвет на основе индекса экземпляра.
        Использует цветовую схему, аналогичную DrawExemplarsPool.

        :param index: индекс экземпляра
        :return: цвет в формате hex
        """
        # Используем ту же логику, что и в DrawExemplarsPool._get_color_from_score
        # Но без оценки - просто разные оттенки
        # Генерируем цвет на основе индекса в HSV пространстве
        hue = (index * 0.618033988749895) % 1.0  # Золотое сечение для равномерного распределения
        saturation = 0.7
        value = 0.8

        # Конвертируем HSV в RGB
        import colorsys
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return f'#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}'

    def _get_exemplar_color(self, exemplar, index: int) -> str:
        """
        Возвращает цвет для экземпляра, используя кэш.

        :param exemplar: объект Exemplar
        :param index: индекс экземпляра в списке
        :return: цвет в формате hex
        """
        # Используем id экземпляра как ключ для кэша
        exemplar_id = id(exemplar)
        if exemplar_id not in self.exemplar_colors:
            self.exemplar_colors[exemplar_id] = self._generate_color_from_index(index)
        return self.exemplar_colors[exemplar_id]

    def clear(self):
        """Очищает графики перед загрузкой новых данных"""
        if self.ax_step:
            self.ax_step.clear()
        if self.ax_exemplars:
            self.ax_exemplars.clear()

        # Очищаем кэш цветов
        self.exemplar_colors.clear()

        # Обнуляем ссылки на старые drawer'ы
        self.draw_step_res = None
        self.draw_exemplars_pool = None
        self.step_res_obj = None

    def reset_data(self, step_res: StepRes):
        """Заполняет канвасы на основе StepRes и записывает ID в текстовое поле."""
        self.step_res_obj = step_res

        # Очищаем кэш цветов перед новой загрузкой
        self.exemplar_colors.clear()

        # Обновляем текстовое поле с ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(step_res.id))

        # Получаем список экземпляров
        exemplars = step_res.get_exemplars()

        # === Верхний канвас: треки шага ===
        # Создаем словарь цветов для передачи в DrawStepRes
        exemplar_color_map = {}
        if exemplars:
            for idx, exemplar in enumerate(exemplars):
                exemplar_color_map[exemplar] = self._get_exemplar_color(exemplar, idx)

        # Передаем карту цветов в DrawStepRes
        self.draw_step_res = DrawStepRes(res_obj=step_res, exemplar_color_map=exemplar_color_map)
        updated_fig_step = self.draw_step_res.get_fig()

        # Заменяем фигуру
        old_figure_step = self.canvas_step.figure
        self.canvas_step.figure = updated_fig_step

        # Закрываем старую фигуру
        if old_figure_step is not None and old_figure_step != updated_fig_step:
            plt.close(old_figure_step)

        self.canvas_step.draw()

        # === Нижний канвас: созданные экземпляры ===
        if exemplars and len(exemplars) > 0:
            # Создаем список цветов для экземпляров в том же порядке
            exemplar_colors_list = []
            for idx, exemplar in enumerate(exemplars):
                exemplar_colors_list.append(self._get_exemplar_color(exemplar, idx))

            # Создаём визуализатор для экземпляров с заданными цветами
            self.draw_exemplars_pool = DrawExemplarsPool(
                exemplars=exemplars,
                exemplar_colors=exemplar_colors_list,
                padding_percent=20,
                show_legend=False
            )
            updated_fig_exemplars = self.draw_exemplars_pool.get_fig()
        else:
            # Если нет экземпляров, показываем пустой график
            self.ax_exemplars.clear()
            self.ax_exemplars.text(0.5, 0.5, 'Нет созданных экземпляров',
                                   horizontalalignment='center',
                                   verticalalignment='center',
                                   transform=self.ax_exemplars.transAxes)
            updated_fig_exemplars = self.figure_exemplars

        # Заменяем фигуру
        old_figure_exemplars = self.canvas_exemplars.figure
        self.canvas_exemplars.figure = updated_fig_exemplars

        # Закрываем старую фигуру
        if old_figure_exemplars is not None and old_figure_exemplars != updated_fig_exemplars:
            plt.close(old_figure_exemplars)

        self.canvas_exemplars.draw()

    def cleanup(self):
        """Очищает ресурсы matplotlib"""
        # Очищаем верхний канвас
        if self.canvas_step:
            self.canvas_step.deleteLater()
        if self.figure_step:
            plt.close(self.figure_step)

        # Очищаем нижний канвас
        if self.canvas_exemplars:
            self.canvas_exemplars.deleteLater()
        if self.figure_exemplars:
            plt.close(self.figure_exemplars)

        # Обнуляем ссылки
        self.figure_step = None
        self.ax_step = None
        self.canvas_step = None
        self.figure_exemplars = None
        self.ax_exemplars = None
        self.canvas_exemplars = None
        self.draw_step_res = None
        self.draw_exemplars_pool = None
        self.step_res_obj = None
        self.exemplar_colors.clear()

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

import sys
from math import sin

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QApplication, QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.visual_debug import TrackRes, PS_Res
from CORE.visual_debug.results_drawers.draw_track_res import DrawTrackRes

# DA3/simulation_app/simulation_widgets/track_full_res_widget.py

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE.visual_debug import TrackRes
from CORE.visual_debug.results_drawers.draw_track_res import DrawTrackRes
from CORE.visual_debug.results_drawers.draw_track_res_SM import DrawTrackRes_SM


class TrackFullResWidget(QWidget):
    """
    Виджет для отображения полной информации о треке:
    - Верхняя часть: отображение трека с SM (DrawTrackRes_SM)
    - Нижняя часть: отображение детального трека (DrawTrackRes)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.track_res_obj = None
        self.draw_track_res_sm = None
        self.draw_track_res = None

        # Фигуры и канвасы
        self.figure_sm = None
        self.ax_sm = None
        self.canvas_sm = None

        self.figure_track = None
        self.ax_track = None
        self.canvas_track = None

        self.init_ui()

    def init_ui(self):
        # Основной layout виджета
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Текстовое поле для ID
        self.id_text_edit = QTextEdit()
        self.id_text_edit.setMaximumHeight(50)
        self.id_text_edit.setReadOnly(True)
        layout.addWidget(QLabel("ID трека (TrackRes):"))
        layout.addWidget(self.id_text_edit)

        # Первый канвас - трек с SM (верхняя часть)
        self.figure_sm, self.ax_sm = plt.subplots(figsize=(10, 4))
        self.canvas_sm = FigureCanvas(self.figure_sm)
        layout.addWidget(self.canvas_sm)

        # Второй канвас - детальный трек (нижняя часть)
        self.figure_track, self.ax_track = plt.subplots(figsize=(10, 4))
        self.canvas_track = FigureCanvas(self.figure_track)
        layout.addWidget(self.canvas_track)

    def clear(self):
        """Очищает графики перед загрузкой новых данных"""
        if self.ax_sm:
            self.ax_sm.clear()
        if self.ax_track:
            self.ax_track.clear()

        # Обнуляем ссылки на старые drawer'ы
        self.draw_track_res_sm = None
        self.draw_track_res = None
        self.track_res_obj = None

    def reset_data(self, track_res: TrackRes):
        """Заполняет канвасы на основе TrackRes и записывает ID в текстовое поле."""
        self.track_res_obj = track_res

        # Обновляем текстовое поле с ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(track_res.id))

        # === Верхний канвас: трек с SM ===
        # Создаём визуализатор для трека с SM
        self.draw_track_res_sm = DrawTrackRes_SM(res_obj=track_res)
        updated_fig_sm = self.draw_track_res_sm.get_fig()

        # Заменяем фигуру
        old_figure_sm = self.canvas_sm.figure
        self.canvas_sm.figure = updated_fig_sm

        # Закрываем старую фигуру
        if old_figure_sm is not None and old_figure_sm != updated_fig_sm:
            plt.close(old_figure_sm)

        self.canvas_sm.draw()

        # === Нижний канвас: детальный трек ===
        # Создаём визуализатор для детального трека
        self.draw_track_res = DrawTrackRes(res_obj=track_res)
        updated_fig_track = self.draw_track_res.get_fig()

        # Заменяем фигуру
        old_figure_track = self.canvas_track.figure
        self.canvas_track.figure = updated_fig_track

        # Закрываем старую фигуру
        if old_figure_track is not None and old_figure_track != updated_fig_track:
            plt.close(old_figure_track)

        self.canvas_track.draw()

    def cleanup(self):
        """Очищает ресурсы matplotlib"""
        # Очищаем верхний канвас
        if self.canvas_sm:
            self.canvas_sm.deleteLater()
        if self.figure_sm:
            plt.close(self.figure_sm)

        # Очищаем нижний канвас
        if self.canvas_track:
            self.canvas_track.deleteLater()
        if self.figure_track:
            plt.close(self.figure_track)

        # Обнуляем ссылки
        self.figure_sm = None
        self.ax_sm = None
        self.canvas_sm = None
        self.figure_track = None
        self.ax_track = None
        self.canvas_track = None
        self.draw_track_res_sm = None
        self.draw_track_res = None
        self.track_res_obj = None


if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Визуализация TrackRes с PS-точками")
            self.setGeometry(100, 100, 800, 600)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Создание тестовых данных
            initial_signal = Signal(signal_mv=[0.1 - sin(i) for i in range(80)], frequency=2)

            # Создаём PS_Res объекты с разными наборами точек
            ps_res_list = [
                PS_Res(
                    id=1,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[11.2, 12.5]
                ),
                PS_Res(
                    id=2,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[10.5, 11.8, 13.2]
                ),
                PS_Res(
                    id=3,
                    signal=initial_signal,
                    left_coord=10.0,
                    right_coord=14.0,
                    res_coords=[12.0, 13.0]  # две точки для третьего PS
                )
            ]

            test_track_res = TrackRes(
                id=42,
                signal=initial_signal,
                left_coord=10.0,
                right_coord=14.0,
                ps_res_objs=ps_res_list,
                sm_res_objs=[]  # SM объекты не нужны для этого виджета
            )

            # Создание виджета TrackResWidget
            self.track_res_widget = TrackFullResWidget()

            # Заполняем виджет данными из тестового TrackRes
            self.track_res_widget.reset_data(test_track_res)

            # Добавляем виджет в layout
            layout.addWidget(self.track_res_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()

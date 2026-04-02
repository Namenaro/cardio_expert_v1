import sys
from math import sin

import matplotlib.pyplot as plt
from PySide6.QtWidgets import QWidget, QLabel, QTextEdit, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from CORE import Signal
from CORE.visual_debug import SM_Res
from CORE.visual_debug.results_drawers.draw_SM_res import DrawSM_Res


class SM_ResWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sm_res_obj = None
        self.draw_sm_res = None

        # Храним ссылки на текущие фигуры и канвасы
        self.figure = None
        self.ax = None
        self.canvas = None

        self.init_ui()

    def init_ui(self):
        # Основной layout виджета
        layout = QVBoxLayout(self)

        # Текстовое поле для ID
        self.id_text_edit = QTextEdit()
        self.id_text_edit.setMaximumHeight(50)
        self.id_text_edit.setReadOnly(True)
        layout.addWidget(QLabel("ID объекта SM_Res:"))
        layout.addWidget(self.id_text_edit)

        # Изначально создаем пустую фигуру
        self._create_new_figure()
        layout.addWidget(self.canvas)

    def _create_new_figure(self):
        """Создает новую фигуру и канвас"""
        # Закрываем старые, если есть
        self._cleanup_figures()

        # Создаем новые
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)

    def _cleanup_figures(self):
        """Закрывает старые фигуры"""
        if self.canvas:
            self.canvas.deleteLater()
            self.canvas = None

        if self.figure:
            plt.close(self.figure)
            self.figure = None
            self.ax = None

    def clear(self):
        """Очищает виджет"""
        self.id_text_edit.clear()

        # Пересоздаем фигуру для очистки
        self._create_new_figure()

        # Обновляем layout с новым канвасом
        if self.canvas:
            # Находим layout и заменяем канвас
            layout = self.layout()
            if layout:
                # Удаляем старый канвас из layout, если он там есть
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and item.widget() == self.canvas:
                        break
                else:
                    # Если канвас не найден, добавляем новый
                    layout.addWidget(self.canvas)

        self.sm_res_obj = None
        self.draw_sm_res = None

    def reset_data(self, sm_res: SM_Res):
        """Заполняет канвас на основе SM_Res и записывает ID в текстовое поле."""
        self.sm_res_obj = sm_res

        # Обновляем текстовое поле с ID
        self.id_text_edit.clear()
        self.id_text_edit.append(str(sm_res.id))

        # Очищаем старые фигуры
        self._cleanup_figures()

        # Создаём визуализатор и получаем фигуру
        self.draw_sm_res = DrawSM_Res(res_obj=sm_res)
        updated_fig = self.draw_sm_res.get_fig()

        # Сохраняем новую фигуру
        self.figure = updated_fig
        self.canvas = FigureCanvas(self.figure)

        # Обновляем layout
        layout = self.layout()
        if layout:
            # Удаляем старый канвас, если есть
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and isinstance(item.widget(), FigureCanvas):
                    old_canvas = item.widget()
                    layout.removeWidget(old_canvas)
                    old_canvas.deleteLater()
                    break

            # Добавляем новый канвас
            layout.addWidget(self.canvas)

    def cleanup(self):
        """Очищает ресурсы matplotlib"""
        self._cleanup_figures()
        self.sm_res_obj = None
        self.draw_sm_res = None


if __name__ == "__main__":
    from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget)


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Layout
            layout = QVBoxLayout(central_widget)

            # Создание тестового сигнала

            test_signal = Signal(signal_mv=[sin(i) for i in range(80)], frequency=2)
            test_signal_2 = Signal(signal_mv=[sin(i) - 0.1 for i in range(80)], frequency=2)
            print(f"Длительность сигнала: {test_signal.get_duration():.2f} секунд")
            print("Сигнал (первые 10 точек):", test_signal.signal_mv[:10])
            print("Время (первые 10 точек):", test_signal.time[:10])

            # Создание тестового SM_Res
            test_sm_res = SM_Res(
                id=1,
                old_signal=test_signal,
                left_coord=10.0,
                right_coord=14.0,
                result_signal=test_signal_2
            )

            # Создание виджета
            self.rs_res_widget = SM_ResWidget()

            # Заполняем виджет данными из тестового SM_Res
            self.rs_res_widget.reset_data(test_sm_res)

            # Добавляем виджет в layout
            layout.addWidget(self.rs_res_widget)


    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


    main()
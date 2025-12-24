import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

from .signal_1d import Signal
from typing import Optional

class Drawer:
    """
    Класс для визуализации 1-d сигналов на миллиметровке.
    Рисует реальные точки данных без сглаживания.
    """

    def __init__(self, ax: plt.Axes):
        self.ax = ax

        self.minor_cell_mv = 0.1
        self.minor_cell_sec = 0.04
        self.major_cell_mv = 0.1
        self.major_cell_sec = 0.2
        self.minor_grid_color = "#f4bfbf"
        self.major_grid_color = "#e37373"

    def draw_signal(self, signal: Signal, color='#202020', name:Optional[str]=None):
        """
        Отрисовывает сигнал.
        Использует маркеры ('o'), чтобы показать реальные точки дискретизации.
        """
        time = np.array(signal.time)
        values = np.array(signal.signal_mv)

        self.ax.plot(
            time, 
            values, 
            color=color, 
            label=name,
            # -------------------------------------
            marker='o',      # кружок на каждой точке
            markersize=0.5,    # размер кружка
            linestyle='-',   # линия между точками
            linewidth=1      # толщина линии
            # -------------------------------------
        )

        self.ax.set_xlabel('Время, с')
        self.ax.set_ylabel('Амплитуда, мВ')
        self.ax.xaxis.set_major_locator(MultipleLocator(self.major_cell_sec))
        self.ax.xaxis.set_minor_locator(MultipleLocator(self.minor_cell_sec))

        self.ax.yaxis.set_major_locator(MultipleLocator(self.major_cell_mv))
        self.ax.yaxis.set_minor_locator(MultipleLocator(self.minor_cell_mv))

        self.ax.grid(True, 'major', color=self.major_grid_color)
        self.ax.grid(True, 'minor', color=self.minor_grid_color, linewidth=0.5)

        if name:
            self.ax.legend()
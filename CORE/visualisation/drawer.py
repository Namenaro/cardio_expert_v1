import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from CORE.signal_1d import Signal

from typing import Optional

class Drawer:
    """
    Класс для визуализации 1-d сигналов на миллиметровке

    Attributes:
        ax: Axes объект matplotlib для отрисовки
    """

    def __init__(self, ax: plt.Axes):
        self.ax = ax

        # Настройки миллиметровки
        self.minor_cell_mv = 0.1
        self.minor_cell_sec = 0.04
        self.major_cell_mv = 0.5
        self.major_cell_sec = 0.2
        self.minor_grid_color = "#f4bfbf"
        self.major_grid_color = "#e37373"

    def draw_signal(self, signal: Signal, color='#202020', name:Optional[str]=None):
        """
        Отрисовывает сигнал на миллиметровке.
        При любом растяжении ax для пользователя миллиметры остаются квадратными.

        Args:
            signal: Объект сигнала для отрисовки
            color: Цвет линии. Может быть:
                  - строкой ('red', 'blue', '#FF0000')
                  - сокращением ('r', 'g', 'b')
                  - RGB кортежем ((1.0, 0.0, 0.0))
                  - None (автоматический выбор)
            name: Название сигнала для легенды
        """
        time = signal.time
        values = signal.signal_mv

        self.ax.plot(time, values, color=color, label=name)

        # Настройка внешнего вида
        self.ax.set_xlabel('Время, с')
        self.ax.set_ylabel('Амплитуда, мВ')

        plt.gca().set_aspect(self.minor_cell_sec/self.minor_cell_mv)

        self.ax.xaxis.set_major_locator(MultipleLocator(self.major_cell_sec))
        self.ax.xaxis.set_minor_locator(MultipleLocator(self.minor_cell_sec))

        self.ax.yaxis.set_major_locator(MultipleLocator(self.major_cell_mv))
        self.ax.yaxis.set_minor_locator(MultipleLocator(self.minor_cell_mv))

        self.ax.grid(True, 'major', color=self.major_grid_color)
        self.ax.grid(True, 'minor', color=self.minor_grid_color, linewidth=0.5)

        if name:
            self.ax.legend()




# Пример использования
if __name__ == "__main__":
    from CORE.datasets.LUDB import LUDB, LEADS_NAMES

    # Загружаем тестовый сигнал
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 1.9)

    # Отрисовываем его
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(signal, color='blue', name='Тестовый сигнал')


    plt.tight_layout()
    plt.show()



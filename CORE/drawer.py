import matplotlib.pyplot as plt
from CORE.signal_1d import Signal

from typing import Optional

class Drawer:
    """
    Класс для визуализации 1-d сигналов на миллиметровке

    Attributes:
        ax: Axes объект matplotlib для отрисовки
    """

    def __init__(self, ax):
        self.ax = ax

        # Настройки миллиметровки TODO
        #self.little_cell_mv = ..
        #self.little_cell_sec = ..
        #self.grid_color =

    def draw_signal(self, signal: Signal, color=None, name:Optional[str]=None):
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

        self.ax.grid(True, alpha=0.3) # TODO

        if name:
            self.ax.legend()




# Пример использования
if __name__ == "__main__":
    from CORE.datasets.LUDB import LUDB, LUDB_LEADS_NAMES

    # Загружаем тестовый сигнал
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LUDB_LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 0.9)

    # Отрисовываем его
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(signal, color='blue', name='Тестовый сигнал')


    plt.tight_layout()
    plt.show()



import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from CORE.signal_1d import Signal


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

    def draw_signal(self, signal: Signal, color='#202020', name=None):
        """
        Отрисовывает сигнал на миллиметровке.
        При любом растяжении ax для пользователя миллиметры остаются квадратными.

        Args:
            signal: Объект сигнала для отрисовки
            color: Цвет линии (по умолчанию автоматический)
            name: Название сигнала для легенды
        """
        time = signal.time
        values = signal.signal_mv

        line = self.ax.plot(time, values, color=color, label=name)[0]

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

        return line


# Пример использования
if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(12, 8))
    drawer = Drawer(ax)

    # Создаем тестовый сигнал
    signal_data = [0.5, 1.2, 0.8, 1.5, 0.3, 1.8, 0.9, 1.0, 1.3, 1.0, 1.3, 1.0]
    signal = Signal(signal_data, frequency=10)  # 10 Гц
    drawer.draw_signal(signal, color='blue', name='Тестовый сигнал')


    plt.tight_layout()
    plt.show()



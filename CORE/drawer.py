import matplotlib.pyplot as plt
from CORE.signal_1d import Signal


class Drawer:
    """
    Класс для визуализации 1-d сигналов на миллиметровке

    Attributes:
        ax: Axes объект matplotlib для отрисовки
    """

    def __init__(self, ax):
        self.ax = ax

        # Настройки миллиметровки
        #self.little_cell_mv=..
        #self.little_cell_sec =..
        #self.grid_color =

    def draw_signal(self, signal: Signal, color=None, name=None):
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

        self.ax.grid(True, alpha=0.3) # TODO

        if name:
            self.ax.legend()

        return line


# Пример использования
if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)

    # Создаем тестовый сигнал
    signal_data = [0.5, 1.2, 0.8, 1.5, 0.3, 1.8, 0.9]
    signal = Signal(signal_data, frequency=10)  # 10 Гц
    drawer.draw_signal(signal, color='blue', name='Тестовый сигнал')


    plt.tight_layout()
    plt.show()



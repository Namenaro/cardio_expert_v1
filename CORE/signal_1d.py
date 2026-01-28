from typing import List, Optional


class Signal:
    """  Представляет одномерный дискретный сигнал с временной разметкой. """
    def __init__(self, signal_mv:List[float], ticks:Optional[List[int]]=None, frequency:int=500):
        """
        :param signal_mv: Значения сигнала в милливольтах
        :param ticks: Номера отсчетов (тиков) сигнала
        :param frequency: Частота дискретизации в Герцах (количество отсчетов в секунду)
        """
        self.signal_mv = signal_mv
        self._ticks = ticks if ticks is not None else list(range(len(signal_mv)))
        self.frequency = frequency


    @property
    def time(self)->List[float]:
        """Возвращает временные метки в секундах, рассчитанные на основе частоты дискретизации."""
        time = [tick/self.frequency for tick in self._ticks]
        return time

    def get_fragment(self, start_time: float, end_time: float) -> 'Signal':
        """Возвращает фрагмент сигнала в заданном временном интервале."""
        if not 0 <= start_time < end_time:
            raise ValueError("Некорректные временные границы")

        indices = [i for i, t in enumerate(self.time) if start_time <= t <= end_time]

        if not indices:
            raise ValueError(f"Интервал [{start_time}, {end_time}) не содержит данных")

        return Signal(
            signal_mv=[self.signal_mv[i] for i in indices],
            ticks=[self._ticks[i] for i in indices],
            frequency=self.frequency
        )

    def is_moment_in_signal(self, t: float) -> bool:
        """
        Проверяет, что момент времени t находится в пределах временных меток сигнала.

        Args:
            t (float): Момент времени в секундах

        Returns:
            bool: True, если момент t находится в диапазоне time, иначе False
        """
        if not self.time:
            return False

        return self.time[0] <= t <= self.time[-1]

    def __len__(self):
        return self.time[-1] - self.time[0]


if __name__ == "__main__":
    from math import sin
    raw_signal = list([sin(i) for i in range(80)])
    test_signal = Signal(signal_mv=raw_signal, frequency=2)


    print(test_signal.signal_mv)
    print(test_signal.time)

    subsignal = test_signal.get_fragment(start_time=20.0, end_time=22.5)
    print(subsignal.signal_mv)
    print(subsignal.time)

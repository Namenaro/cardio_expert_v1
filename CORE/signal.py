from typing import List, Optional


class Signal:
    def __init__(self, signal_mv:List[float], ticks:Optional[List[int]]=None, frequency:int=500):
        """
            Представляет одномерный дискретный сигнал с временной разметкой.

            Attributes:
                _signal_mv (List[float]): Значения сигнала в милливольтах
                _ticks (List[int]): Номера отсчетов (тиков) сигнала
                frequency (int): Частота дискретизации в Герцах (количество отсчетов в секунду)

        """
        self._signal_mv = signal_mv
        self._ticks = ticks if ticks is not None else list(range(len(signal_mv)))
        self.frequency = frequency

    @property
    def signal_mv(self)->List[float]:
        """Возвращает значения сигнала в милливольтах."""
        return self._signal_mv

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
            signal_mv=[self._signal_mv[i] for i in indices],
            ticks=[self._ticks[i] for i in indices],
            frequency=self.frequency
        )

if __name__ == "__main__":
    from math import sin
    raw_signal = list([sin(i) for i in range(80)])
    test_signal = Signal(signal_mv=raw_signal, frequency=2)

    print(test_signal.signal_mv)
    print(test_signal.time)

    subsignal = test_signal.get_fragment(start_time=20.0, end_time=22.5)
    print(subsignal.signal_mv)
    print(subsignal.time)

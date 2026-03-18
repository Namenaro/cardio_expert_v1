from typing import List, Optional

import bisect

from CORE.utils import find_closest_sorted


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
        :param t (float) Момент времени в секундах
        :return: bool  True, если момент t находится в диапазоне time, иначе False
        """
        if not self.time:
            return False

        return self.time[0] <= t <= self.time[-1]


    def get_amplplitude_in_moment(self, time_moment_sec) -> Optional[float]:
        """
        Получить значение сигнала в момент времени time_moment_sec.
        Примечание: находим ближайший к интересующему нас моменту отсчет, для каторого значение сигнала известно
        :param time_moment_sec: момент времени, в секундах
        :return: значение сигнала в mV
        """
        if not self.is_moment_in_signal(time_moment_sec):
            return None
        nearest_index = find_closest_sorted(self.time, time_moment_sec=time_moment_sec)
        amplitude = self.signal_mv[nearest_index]
        return amplitude

    def get_cropped_with_padding(self, coord_left: float, coord_right: float, padding_percent: float) -> 'Signal':
        """
        Возвращает фрагмент сигнала с отступами (padding) слева и справа.

        :param coord_left (float) Левая граница интересующего интервала в секундах
        :param coord_right (float) Правая граница интересующего интервала в секундах
        :param padding_percent (float)  Процент от длины запрашиваемого интервала, который будет
                                    распределен поровну на левый и правый отступы

        :return: Signal: Новый сигнал с добавленными отступами
        """
        # Проверка входных параметров
        if not 0 <= coord_left < coord_right:
            raise ValueError("Некорректные временные границы")

        if padding_percent < 0:
            raise ValueError("Процент паддинга не может быть отрицательным")

        if not self.time:
            raise ValueError("Сигнал не содержит данных")

        # Длина запрашиваемого интервала в секундах
        interval_duration = coord_right - coord_left

        # Рассчитываем величину отступа в секундах
        # padding_percent - это процент от длины запрашиваемого интервала,
        # который будет добавлен в сумме слева и справа
        total_padding = interval_duration * (padding_percent / 100.0)
        half_padding = total_padding / 2.0

        # Рассчитываем границы с учетом паддинга
        padded_left = coord_left - half_padding
        padded_right = coord_right + half_padding

        # Корректируем границы, чтобы не выходить за пределы сигнала
        padded_left = max(padded_left, self.time[0])
        padded_right = min(padded_right, self.time[-1])

        # Проверяем, что после корректировки границы остались корректными
        if padded_left >= padded_right:
            # Если интервал стал пустым, возвращаем сигнал из одной точки
            # или выбрасываем исключение
            raise ValueError("После корректировки паддинга интервал не содержит данных")

        # Вырезаем фрагмент с рассчитанными границами
        return self.get_fragment(padded_left, padded_right)

    def get_duration(self) -> float:
        """Возвращает длительность сигнала в секундах."""
        if len(self.time) < 2:
            return 0.0
        return self.time[-1] - self.time[0]

    def __len__(self):
        """Возвращает количество отсчетов в сигнале"""
        return len(self.signal_mv)




if __name__ == "__main__":
    from math import sin
    raw_signal = list([sin(i) for i in range(80)])
    test_signal = Signal(signal_mv=raw_signal, frequency=2)
    print(f"Длительность сигнала: {test_signal.get_duration():.2f} секунд")


    print(test_signal.signal_mv)
    print(test_signal.time)

    subsignal = test_signal.get_fragment(start_time=20.0, end_time=22.5)
    print(subsignal.signal_mv)
    print(subsignal.time)

    fragment1 = test_signal.get_cropped_with_padding(
        coord_left=10.0,
        coord_right=15.0,
        padding_percent=20  # 20% от длины интервала
    )
    interval_length = 15.0 - 10.0
    print(f"Фрагмент 1 (паддинг 20%):")
    print(f"  Исходный интервал: [10.0, 15.0] (длина {interval_length:.1f} сек)")
    print(f"  Результирующий интервал: [{fragment1.time[0]:.2f}, {fragment1.time[-1]:.2f}]")
    print(f"  Длина: {fragment1.get_duration():.2f} сек")

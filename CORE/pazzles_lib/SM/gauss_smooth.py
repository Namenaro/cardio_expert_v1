import numpy as np

from CORE.pazzles_lib.sm_base import SMBase
from CORE.signal_1d import Signal
from copy import deepcopy
from CORE.signal_1d import Signal
from copy import deepcopy
from typing import Optional
import numpy as np
from scipy.signal import convolve

from typing import Optional


class GaussianSmooth(SMBase):
    """ Сглаживание сигнала гауссовым ядром"""

    def __init__(self, sigma: float = 2.5, kernel_size_t: float = 0.3):
        """
        :param sigma: Стандартное отклонение гауссова ядра.
        :param kernel_size_t:  Размер ядра фильтра. Измеряется в секундах
        """
        self.sigma = sigma
        self.kernel_size_int = kernel_size_t

    def run(self, signal: Signal, left_t:Optional[float]=None, right_t:Optional[float]=None) -> Signal:
        res_signal = deepcopy(signal)
        sampling_rate = res_signal.frequency

        # Переводим секунды в отсчеты
        if left_t is not None:
            left_idx = int(left_t * sampling_rate)
        else:
            left_idx = 0

        if right_t is not None:
            right_idx = int(right_t * sampling_rate)
        else:
            right_idx = len(res_signal.signal_mv)

        # Проверяем границы
        left_idx = max(0, left_idx)
        right_idx = min(len(res_signal.signal_mv), right_idx)

        if left_idx >= right_idx:
            return res_signal

        # Создаем гауссово ядро
        kernel_size_samples = int(self.kernel_size_int * sampling_rate)

        # Корректируем размер ядра при необходимости
        if kernel_size_samples >= (right_idx - left_idx) or kernel_size_samples < 1:
            return res_signal

        # Гарантируем нечетность ядра
        if kernel_size_samples % 2 == 0:
            kernel_size_samples -= 1
        if kernel_size_samples < 3:
            kernel_size_samples = 3

        # Создаем гауссово ядро
        x = np.linspace(-kernel_size_samples // 2, kernel_size_samples // 2, kernel_size_samples)
        kernel = np.exp(-x ** 2 / (2 * self.sigma ** 2))
        kernel = kernel / np.sum(kernel)  # нормализуем

        # Выделяем часть сигнала для сглаживания
        signal_to_smooth = res_signal.signal_mv[left_idx:right_idx]

        # Добавляем границы для минимизации краевых эффектов
        pad_width = kernel_size_samples // 2

        # Если слева от участка есть данные, используем их для padding
        if left_idx > 0:
            left_pad = res_signal.signal_mv[max(0, left_idx - pad_width):left_idx]
        else:
            left_pad = signal_to_smooth[:pad_width][::-1]  # зеркальное отражение

        # Если справа от участка есть данные, используем их для padding
        if right_idx < len(res_signal.signal_mv):
            right_pad = res_signal.signal_mv[right_idx:min(len(res_signal.signal_mv), right_idx + pad_width)]
        else:
            right_pad = signal_to_smooth[-pad_width:][::-1]  # зеркальное отражение

        # Собираем сигнал с padding
        padded_signal = np.concatenate([left_pad, signal_to_smooth, right_pad])

        # Проводим свертку
        smoothed_padded = convolve(padded_signal, kernel, mode='same', method='auto')

        # Извлекаем центральную часть (без padding)
        smoothed_part = smoothed_padded[len(left_pad):len(left_pad) + len(signal_to_smooth)]

        # Обновляем только указанную часть сигнала
        res_signal.signal_mv[left_idx:right_idx] = smoothed_part.tolist()

        return res_signal


# Пример использования
if __name__ == "__main__":
    from CORE.visualisation.signal_1d_drawer import Signal_1D_Drawer
    from CORE.datasets_wrappers.LUDB import LUDB, LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[10], lead_name=LEADS_NAMES.i)
    old_signal = signal.get_fragment(0.0, 0.9)

    # Создаем паззл
    gs = GaussianSmooth()
    # Левая и правая границы заданы в секундах (в данном случае выше выбран фрагмент от 0 до 0.9),
    # а в методе run они преобразуются в индексы
    new_signal = gs.run(signal=old_signal, left_t=0.3, right_t=0.7)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Signal_1D_Drawer(ax)
    drawer.draw_signal(new_signal, name="new", color='blue')
    drawer.draw_signal(old_signal, name="old")
    plt.show()


 
import numpy as np
from scipy.signal import convolve

from CORE.signal_1d import Signal
from copy import deepcopy

from typing import Optional


class GaussianSmooth:
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

        # переводим секунды в дискреты
        sampling_rate = res_signal.frequency
        kernel_size_samples = int(self.kernel_size_int * sampling_rate)

        # Проверяем размер ядра
        if kernel_size_samples >= len(res_signal.signal_mv) or kernel_size_samples < 1:
            return res_signal

        # проверяем границы
        if kernel_size_samples > len(res_signal.signal_mv):
            kernel_size_samples = len(res_signal.signal_mv) - 1
            if kernel_size_samples % 2 == 0:
                kernel_size_samples -= 1  # гарантируем нечетность

        if kernel_size_samples < 3:
            return res_signal

        # создаем гауссово ядро
        x = np.linspace(-kernel_size_samples // 2, kernel_size_samples // 2, kernel_size_samples)
        kernel = np.exp(-x ** 2 / (2 * self.sigma ** 2))
        kernel = kernel / np.sum(kernel)  # нормализуем

        # проводим свертку сигнала
        smoothed_signal = convolve(res_signal.signal_mv, kernel, mode='same', method='auto')

        res_signal.signal_mv = smoothed_signal.tolist()

        return res_signal


# Пример использования
if __name__ == "__main__":
    from CORE.drawer import Drawer
    from CORE.datasets.LUDB import LUDB, LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LEADS_NAMES.i)
    old_signal = signal.get_fragment(0.0, 0.9)

    # Создаем паззл
    gs = GaussianSmooth()
    new_signal = gs.run(signal=old_signal)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(new_signal, name="new", color='red')
    drawer.draw_signal(old_signal, name="old")
    plt.show()


 
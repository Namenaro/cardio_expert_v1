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
        # учитываем нечетность количества дискретов в ядре
        # проверяем границы
        # проводим свертку сигнала res_signal.signal_mV
        return res_signal


# Пример использования
if __name__ == "__main__":
    from CORE.drawer import Drawer
    from CORE.datasets.LUDB import LUDB, LUDB_LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LUDB_LEADS_NAMES.i)
    old_signal = signal.get_fragment(0.0, 0.9)

    # Создаем паззл
    gs = GaussianSmooth()
    new_signal = gs.run(signal=old_signal)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(new_signal, name="new")
    drawer.draw_signal(old_signal, name="old")
    plt.show()


 
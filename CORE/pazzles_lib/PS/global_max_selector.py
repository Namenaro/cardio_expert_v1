from CORE.signal_1d import Signal
from copy import deepcopy

from typing import Optional, List


class GlobalMaxSelector:
    """ Глобальный максимум на интервале"""

    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> List[float]:
        ts_indices = [t for t, x in enumerate(signal.signal_mv) if x == max(signal.signal_mv)]          # finding indices of global max points
        ts_of_maxs = [signal.time[t] for t in ts_indices]                                               # matching points indices with timestamps
        print(ts_of_maxs)
        return ts_of_maxs


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

    # Создаем паззл3
    gms = GlobalMaxSelector()
    t_moments = gms.run(signal=old_signal, left_t=0.1, right_t=0.3)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(old_signal)
    for t_moment in t_moments:
        ax.axvline(x=t_moment, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)
    plt.show()

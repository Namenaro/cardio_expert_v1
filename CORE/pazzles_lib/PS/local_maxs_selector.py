from typing import Optional, List
import numpy as np
from scipy.signal import find_peaks

from CORE.signal_1d import Signal


class LocalMaxsSelector:
    """Все локальные максимумы на интервале"""

    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> List[float]:
        # Обработка пустых left_t и right_t
        if left_t is None:
            left_t = signal.time[0]
        if right_t is None:
            right_t = signal.time[-1]
        interval = signal.get_fragment(left_t, right_t)

        inds_of_maxs = find_peaks(np.array(interval.signal_mv), threshold=1e-4)[0]
        ts_of_maxs = [interval.time[x] for x in inds_of_maxs]
        return ts_of_maxs


# Пример использования
if __name__ == "__main__":
    from CORE.visualisation import Signal_1D_Drawer
    from CORE.datasets_wrappers.LUDB import LUDB, LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[3], lead_name=LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 0.9)

    # Создаем паззл
    lms = LocalMaxsSelector()
    t_moments = lms.run(signal=signal)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 8))
    drawer = Drawer(ax)
    drawer.draw_signal(signal)
    for t_moment in t_moments:
        ax.axvline(x=t_moment, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)
    plt.show()

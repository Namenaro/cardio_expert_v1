from CORE.signal_1d import Signal

from typing import Optional, List


class GlobalMinSelector:
    """ Глобальный минимум на интервале"""

    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> List[float]:
        # Переводим left_t и right_t в индексы
        if left_t is None or left_t not in signal.time:
            left_t = signal.time[0]
        if right_t is None or right_t not in signal.time:
            right_t = signal.time[-1]
        left_i = signal.time.index(left_t)
        right_i = signal.time.index(right_t)

        # Находим индексы точек глобального минимума
        ts_indices = [t for t, x in enumerate(signal.signal_mv) if x == min(signal.signal_mv[left_i:right_i+1]) and t in range(left_i, right_i+1)]

        # По индексам восстанавливаем точки во времени
        ts_of_mins = [signal.time[t] for t in ts_indices]

        return ts_of_mins


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
    gms = GlobalMinSelector()
    t_moments = gms.run(signal=old_signal, left_t=0.4, right_t=0.8)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(old_signal)
    for t_moment in t_moments:
        ax.axvline(x=t_moment, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)
    plt.show()

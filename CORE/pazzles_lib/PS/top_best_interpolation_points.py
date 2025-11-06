from typing import Optional, List

from CORE.signal_1d import Signal


class TopBestInterpolationPoints:
    """ Топ N вариантов, как поставить одну точку так, чтобы линейная интерполяция через нее привела к наименьшему расхождению с реальным сигналом"""

    def __init__(self, N: int = 3):
        """
        :param N: сколько надо кандидатов (штук), вернем их упорядоченными по качеству от лучшего к худшему
        """
        self.N = 3

    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> List[float]:
        ts_of_best = [0.3, 0.4, 0.5]
        return ts_of_best


# Пример использования
if __name__ == "__main__":
    from CORE.drawer import Drawer
    from CORE.datasets.LUDB import LUDB, LUDB_LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LUDB_LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 0.9)

    # Создаем паззл
    ps = TopBestInterpolationPoints(N=3)
    t_moments = ps.run(signal=signal)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(signal)
    for t_moment in t_moments:
        ax.axvline(x=t_moment, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)
    plt.show()

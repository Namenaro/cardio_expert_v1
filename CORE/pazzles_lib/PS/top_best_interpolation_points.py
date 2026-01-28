from typing import Optional, List
import numpy as np

from CORE.pazzles_lib.ps_base import PSBase
from CORE.signal_1d import Signal


class TopBestInterpolationPoints(PSBase):
    """ Топ N вариантов, как поставить одну точку так, чтобы линейная интерполяция через нее привела к наименьшему расхождению с реальным сигналом"""

    def __init__(self, N: int = 3):
        """
        :param N: сколько надо кандидатов (штук), вернем их упорядоченными по качеству от лучшего к худшему
        """
        self.N = N

    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> List[float]:
        # Обработка пустых left_t и right_t
        if left_t is None:
            left_t = signal.time[0]
        if right_t is None:
            right_t = signal.time[-1]
        interval = signal.get_fragment(left_t, right_t)

        # Переводим временные отрезки и импульсы в точки в двумерном пространстве
        points = [(x, y) for x, y in list(zip(interval.time, interval.signal_mv))]

        # Метод линейной интерполяции
        def interpolate(x, a, b):
            x1, y1 = a
            x2, y2 = b
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

        # Вычисляем среднеквадратичную ошибку в каждой точке
        mses = []
        for i in range(len(interval.time)):
            sum_error = 0.0
            for (x, y) in points[1:i]:
                y_interp = interpolate(x, points[1], points[i])
                sum_error += (y - y_interp) ** 2
            for (x, y) in points[i + 1:len(interval.time)]:
                y_interp = interpolate(x, points[i], points[len(interval.time) - 1])
                sum_error += (y - y_interp) ** 2
            mses.append(np.mean(sum_error))

        # Выбираем N лучших кандидатов
        ts_indices = np.argsort(mses)[:self.N]
        ts_of_best = [interval.time[t] for t in ts_indices]
        return ts_of_best


# Пример использования
if __name__ == "__main__":
    from CORE.visualisation.signal_1d_drawer import Signal_1D_Drawer
    from CORE.datasets_wrappers.LUDB import LUDB, LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 0.9)

    # Создаем паззл
    ps = TopBestInterpolationPoints(N=3)
    t_moments = ps.run(signal=signal, left_t = 0.8, right_t = 0.82)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Signal_1D_Drawer(ax)
    drawer.draw_signal(signal)
    for t_moment in t_moments:
        ax.axvline(x=t_moment, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)
    plt.show()

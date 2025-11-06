from CORE.signal_1d import Signal
from copy import deepcopy

from typing import Optional


class GlobalMaxSelector:
    """ Сглаживание сигнала гауссовым ядром"""

    def run(self, signal: Signal, left_t:Optional[float]=None, right_t:Optional[float]=None) -> float:
        t_of_max=0.3
        return t_of_max


if __name__ == "__main__":
    from CORE.drawer import Drawer
    from CORE.datasets.LUDB import LUDB, LUDB_LEADS_NAMES

    import matplotlib.pyplot as plt

    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()

    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LUDB_LEADS_NAMES.i)
    old_signal = signal.get_fragment(0.0, 0.9)


    gms =GlobalMaxSelector()
    t_moment = gms.run(signal=old_signal)
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)

    drawer.draw_signal(old_signal)
    ax.axvline(x=t_moment, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)

    plt.show()
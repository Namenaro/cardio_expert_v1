from CORE.pazzles_lib.pc_base import PCBase
from CORE.signal_1d import Signal
from typing import Optional, Any, Dict
from dataclasses import dataclass, field


class AmplitudeInPoint(PCBase):
    """ Просто значение сигнала в точке"""

    # Схема выходных данных
    OUTPUT_SCHEMA = {
        'amplitude_mV': (float, "Значение сигнала в точке")
    }

    def register_points(self, my_point: float) -> None:
        """
        :param my_point: точка в которой мерим значение сигнала

        """
        self.point = my_point

    def register_input_parameters(self):
        """
        Этому классу не нужны другие параметры
        """
        pass

    def run(self, signal: Signal) -> Dict[str, Any]:
        return {'amplitude_mV': signal.get_amplplitude_in_moment(self.point)}


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
    pc = AmplitudeInPoint()

    p1 = 0.3

    pc.register_points(my_point=p1)
    out_params = pc.run(signal=signal)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Signal_1D_Drawer(ax)
    drawer.draw_signal(signal)
    ax.axvline(x=p1, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)

    plt.show()

    print(f"res = {out_params}")

from CORE.pazzles_lib.pc_base import PCBase
from CORE.signal_1d import Signal
from typing import Optional, Any, Dict
from dataclasses import dataclass, field


class Minus(PCBase):
    """ Разность двух чисел num2 - num1"""

    # Схема выходных данных
    OUTPUT_SCHEMA = {
        'num2-num1': (float, "значение разности num2 - num1 "),

    }

    def register_points(self) -> None:
        pass

    def register_input_parameters(self, num1: float, num2: float):
        """
        :param num2: из чего вычитаем
        :param num1: что вычитаем
        :return:
        """
        self.num1 = num1
        self.num2 = num2

    def run(self, signal: Signal) -> Dict[str, Any]:
        res = self.num2 - self.num1
        return {
            'num2-num1': res
        }


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
    pc = Minus()
    pc.register_input_parameters(num1=9, num2=5)

    out_params = pc.run(signal=signal)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Signal_1D_Drawer(ax)
    drawer.draw_signal(signal)

    plt.show()

    print(f"res = {out_params}")

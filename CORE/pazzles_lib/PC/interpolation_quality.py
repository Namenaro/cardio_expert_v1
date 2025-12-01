from CORE.signal_1d import Signal
from typing import Optional
from dataclasses import dataclass, field


class InterpolationError:
    """ Если построить лин.интерполяцию по 2 точкам (левая,  правая),
    то какое расхождение будет с сигналом внутри этого промежутка"""

    @dataclass
    class OutputParams:
        error_in_procents: float = field(metadata={"description": "Ошибка интерполяции в процентах"})
        error_in_mV: float =field(metadata={"description": "Ошибка интерполяции в мв"})

    def register_points(self, point_left:float, point_right:float):
        """
        :param point_left: левая точка
        :param point_right: правая точка
        """
        self.point_left = point_left
        self.point_right = point_right


    def register_input_parameters(self, some_example_param:bool):
        """
        :param some_example_param: блаблабла
        :return:
        """
        self.some_example_param = some_example_param  # TODO удалить потом, а пока чисто для теста парсера


    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> 'InterpolationError.OutputParams':
        # строим интерполяцию, считаем ошибку....
        err_in_mV = 8.3
        err_in_procents = 0.11

        return self.OutputParams(
            error_in_mV=err_in_mV,
            error_in_procents=err_in_procents
        )

# Пример использования
if __name__ == "__main__":
    from CORE.drawer import Drawer
    from CORE.datasets.LUDB import LUDB, LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 0.9)

    # Создаем паззл
    pc = InterpolationError()
    pc.register_input_parameters(some_example_param=True)
    p1=0.3
    p3=0.5
    pc.register_points(point_left=p1, point_right=p3)
    out_params = pc.run(signal=signal)

    # Визуализация
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)
    drawer.draw_signal(signal)
    ax.axvline(x=p1, ymin=0, ymax=1, color='r', linestyle='--', linewidth=1)
    ax.axvline(x=p3, ymin=0, ymax=1, color='b', linestyle='--', linewidth=1)
    plt.show()

    print(f"res = {out_params}")
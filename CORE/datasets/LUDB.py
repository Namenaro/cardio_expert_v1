from CORE.signal_1d import Signal

from importlib import resources
import json
from typing import Optional, List
from types import SimpleNamespace

LUDB_LEADS_NAMES = SimpleNamespace(
    i='i',
    ii='ii',
    iii='iii',
    avr='avr',
    avl='avl',
    avf='avf',
    v1='v1',
    v2='v2',
    v3='v3',
    v4='v4',
    v5='v5',
    v6='v6',
)


class LUDB:
    def __init__(self):
        """
            Обертка для работы с датасетом LUDB.
            Загружает данные из JSON-файла и предоставляет методы для доступа к ним.

            Attributes:
                _data (dict): Загруженные данные датасета

            Raises:
                FileNotFoundError: Если файл датасета не найден
            """
        try:
            with resources.files('CORE.datasets.data').joinpath('ecg_data_200.json').open('r', encoding='utf-8') as f:
                self._data = json.load(f)

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Файл датасета 'ludb.json' не найден в пакете 'datasets.data'"
            ) from e

    def get_1d_signal(self, patient_id:str, lead_name:LUDB_LEADS_NAMES)->Optional[Signal]:
        """
                Возвращает одномерный сигнал для указанного пациента и отведения.

                Args:
                    patient_id: Идентификатор пациента в файле ecg_data_200.json
                    lead_name: Название отведения из LUDB_LEADS_NAMES

                Returns:
                    Объект Signal с данными сигнала или None,
                    если сигнал не найден

                Note:
                    Исходные данные в LUDB представлены в мквольтах, поэтому при создании Signal
                    выполняется преобразование в милливольты
        """
        signal_mkV= self._data[patient_id]['Leads'][lead_name]['Signal']
        signal_mV = [s / 1000 for s in signal_mkV]
        signal = Signal(signal_mv=signal_mV)
        return signal

    def get_patients_ids(self)->List[str]:
        return list(self._data.keys())

if __name__ == "__main__":
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()

    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LUDB_LEADS_NAMES.i)
    print(signal.time[0:8])

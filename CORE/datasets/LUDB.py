import os

from CORE.datasets.third_party_dataset import ThirdPartyDataset
from CORE.enums import LEADS_NAMES
from CORE.signal_1d import Signal

from importlib import resources
import json
from typing import Optional, List
from CORE.paths import LUDB_JSON_PATH


class LUDB(ThirdPartyDataset):
    def __init__(self):
        """
            Обертка для работы с датасетом LUDB.
            Загружает данные из JSON-файла и предоставляет методы для доступа к ним.

            Attributes:
                _data (dict): Загруженные данные датасета

            Raises:
                FileNotFoundError: Если файл LUDB_JSON_PATH не найден.
                json.JSONDecodeError: Если файл содержит некорректный JSON.
            """
        if not os.path.exists(LUDB_JSON_PATH):
            raise FileNotFoundError(f"Файл LUDB не найден: {LUDB_JSON_PATH}")

        try:
            with open(LUDB_JSON_PATH, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Ошибка парсинга JSON в файле {LUDB_JSON_PATH}: {e}", e.doc, e.pos
            ) from e

    def get_1d_signal(self, patient_id:str, lead_name:LEADS_NAMES)->Optional[Signal]:
        """
                Возвращает одномерный сигнал для указанного пациента и отведения.

                Args:
                    patient_id: Идентификатор пациента в файле ecg_data_200.json
                    lead_name: Название отведения из enums.py

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
        return list(self._data.keys()) if self._data else []

if __name__ == "__main__":
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    print(f" Пациентов найдено {len(patients_ids)}")

    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LEADS_NAMES.i)
    print(signal.time[0:8])

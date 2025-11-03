from CORE.signal_1d import Signal

from importlib import resources
import json
from typing import Optional
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


class LUDB_wrapper:
    def __init__(self):
        """
            Обертка для работы с датасетом LUDB.
            Загружает данные из JSON-файла и предоставляет методы для доступа к ним.

            Attributes:
                data (dict): Загруженные данные датасета

            Raises:
                FileNotFoundError: Если файл датасета не найден
            """
        try:
            with resources.files('datasets.data').joinpath('ludb.json').open('r', encoding='utf-8') as f:
                self.data = json.load(f)

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Файл датасета 'ludb.json' не найден в пакете 'datasets.data'"
            ) from e

    def get_signal(self, patient_id:str, lead_name:LUDB_LEADS_NAMES)->Optional[Signal]:
        pass

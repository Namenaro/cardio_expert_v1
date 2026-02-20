from pathlib import Path
import json
import os
from typing import List, Optional, Dict

from CORE.datasets_wrappers.third_party_dataset import ThirdPartyDataset
from CORE.db_dataclasses import Form
from CORE.paths import EXEMPLARS_DATASETS_PATH
from CORE.logger import get_logger
from CORE.datasets_wrappers.form_associated.raw_entry import RawEntry
from CORE.run import Exemplar

from CORE.logger import get_logger

logger = get_logger(__name__)


class ExemplarsDataset:
    """
    Класс, который на основе датасета с сырой разметкой точек генерирует
    словарь объектов класса Exemplar.
    Ключ словаря совпадает с ключом записей в датасете сырых записей.
    Если предоставлен объект формы, то экземпляры содержат не отолько точки,
    но и параметры, и сведения о проваленных условиях формы
    """

    def __init__(self, form_dataset_name: str, outer_dataset: ThirdPartyDataset):
        self.form_dataset_name = form_dataset_name
        self.outer_dataset = outer_dataset  # Внешний датасет, на сигналах которого производилась наша разметка экземпляров формы
        self.point_names: List[str] = []  # Имена точек формы
        self.exemplars: Dict[str, Exemplar] = {}  # Размеченные нами вручную экземпляры

        full_path = os.path.join(EXEMPLARS_DATASETS_PATH, form_dataset_name)
        self._load_data(full_path)

    def _entry_to_exemplar(self, entry: RawEntry) -> Optional[Exemplar]:
        # Находим силнал этого отведения этого пациента
        signal = self.outer_dataset.get_1d_signal(patient_id=entry.patient_id, lead_name=entry.lead_name)

        # Заполняем точки
        exemplar = Exemplar(signal)
        for point_name, point_coord in entry.points.items():
            exemplar.add_point(point_name=point_name, point_coord_t=point_coord, track_id=None)

        return exemplar

    def _load_data(self, filepath: str):
        """Загрузка данных из JSON файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Получаем метаинформацию
            self.point_names = data.get('meta', {}).get('points', [])

            # Загружаем записи
            data_dict = data.get('data', {})
            for entry_id, entry_data in data_dict.items():
                entry = RawEntry.from_dict(entry_id, entry_data)
                exemplar = self._entry_to_exemplar(entry)
                self.exemplars[entry_id] = exemplar

            logger.info(f"Загружено {len(self.exemplars)} записей")

        except Exception as e:
            logger.error(f"Ошибка загрузки {filepath}: {e}")
            raise

    def get_exemplar_by_id(self, id: str) -> Optional[Exemplar]:
        """Получение записи по ID"""
        return self.exemplars.get(id)

    def get_all_ids(self) -> List[str]:
        """Получение всех ID"""
        return list(self.exemplars.keys())

    def __len__(self) -> int:
        """Количество записей"""
        return len(self.exemplars)

    def __contains__(self, id: str) -> bool:
        """Проверка наличия ID"""
        return id in self.exemplars


if __name__ == "__main__":
    from CORE.datasets_wrappers import LUDB

    ludb = LUDB()
    dataset = ExemplarsDataset(form_dataset_name="test_form_dataset.json", outer_dataset=ludb)
    print(f" датасет точек без параметризации: {len(dataset)}")

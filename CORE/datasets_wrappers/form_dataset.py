from pathlib import Path
import json
import os
from typing import List, Optional, Dict

from CORE.datasets_wrappers.third_party_dataset import ThirdPartyDataset
from CORE.db_dataclasses import Form
from CORE.paths import DB_PATH, EXEMPLARS_DATASETS_PATH
from CORE.logger import get_logger
from CORE.datasets_wrappers.form_dataset_entry import Entry

logger = get_logger(__name__)


class FormDataset:
    def __init__(self, form_dataset_name: str, outer_dataset: ThirdPartyDataset, form: Form):
        self.form = form
        self.outer_dataset = outer_dataset
        self.point_names: List[str] = []
        self._entries: Dict[str, Entry] = {}

        full_path = os.path.join(EXEMPLARS_DATASETS_PATH, form_dataset_name)
        self._load_data(full_path)

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
                entry = Entry.from_dict(entry_id, entry_data)
                self._entries[entry_id] = entry

            logger.info(f"Загружено {len(self._entries)} записей")

        except Exception as e:
            logger.error(f"Ошибка загрузки {filepath}: {e}")
            raise

    def get_exemplar_by_id(self, id: str) -> Optional[Entry]:
        """Получение записи по ID"""
        return self._entries.get(id)

    def get_all_ids(self) -> List[str]:
        """Получение всех ID"""
        return list(self._entries.keys())

    def __len__(self) -> int:
        """Количество записей"""
        return len(self._entries)

    def __contains__(self, id: str) -> bool:
        """Проверка наличия ID"""
        return id in self._entries

    def __getitem__(self, id: str) -> Entry:
        """Доступ по ID через квадратные скобки"""
        if id not in self._entries:
            raise KeyError(f"Запись {id} не найдена")
        return self._entries[id]

if __name__ == "__main__":
    from CORE.datasets_wrappers import LUDB

    # TODO mock Form
    ludb = LUDB()
    dataset = FormDataset(forms_dataset_name="test_form_dataset.json")

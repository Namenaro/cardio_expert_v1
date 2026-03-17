import json
import os
from typing import List, Optional, Dict

from CORE.datasets_wrappers.form_associated.raw_entry import RawEntry
from CORE.datasets_wrappers.third_party_dataset import ThirdPartyDataset
from CORE.logger import get_logger
from CORE.paths import EXEMPLARS_DATASETS_PATH
from CORE.run import Exemplar

logger = get_logger(__name__)


class ExemplarsDataset:
    """
    Класс, который на основе датасета с сырой разметкой точек генерирует
    словарь объектов класса Exemplar.
    Ключ словаря совпадает с ключом записей в датасете сырых записей.
    Если предоставлен объект формы, то экземпляры содержат не только точки,
    но и параметры, и сведения о проваленных условиях формы
    """

    def __init__(self, form_dataset_name: str, outer_dataset: ThirdPartyDataset):
        self.form_dataset_name = form_dataset_name
        self.outer_dataset = outer_dataset  # Внешний датасет, на сигналах которого производилась наша разметка экземпляров формы
        self.point_names: List[str] = []  # Имена точек формы
        self.exemplars: Dict[str, Exemplar] = {}  # Размеченные нами вручную экземпляры

        full_path = os.path.join(EXEMPLARS_DATASETS_PATH, form_dataset_name)
        logger.info(f"Загрузка датасета из: {full_path}")
        self._load_data(full_path)

    def _entry_to_exemplar(self, entry: RawEntry) -> Optional[Exemplar]:
        """Преобразование RawEntry в Exemplar"""
        # Получаем сигнал
        signal = self.outer_dataset.get_1d_signal(
            patient_id=entry.patient_id,
            lead_name=entry.lead_name
        )

        if signal is None:
            logger.warning(f"Сигнал не найден: patient={entry.patient_id}, lead={entry.lead_name}")
            return None

        # Создаем Exemplar и добавляем точки
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

            if not data_dict:
                logger.warning(f"Датасет {filepath} не содержит записей")
                return

            for entry_id, entry_data in data_dict.items():
                # Создаем RawEntry из словаря
                entry = RawEntry.from_dict(entry_id, entry_data)

                # Преобразуем в Exemplar
                exemplar = self._entry_to_exemplar(entry)

                if exemplar:
                    self.exemplars[entry_id] = exemplar

            logger.info(f"Загружено {len(self.exemplars)} записей из {filepath}")

        except FileNotFoundError:
            logger.error(f"Файл не найден: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON в {filepath}: {e}")
            raise
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

    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАГРУЗКИ ДАТАСЕТА")
    print("=" * 60)

    ludb = LUDB()
    print(f"LUDB загружен, пациентов: {len(ludb.get_patients_ids())}")

    dataset = ExemplarsDataset(form_dataset_name="qrs.json", outer_dataset=ludb)
    print(f"\nДатасет точек: {len(dataset)} записей")

    if len(dataset) > 0:
        print("\nПервые 5 ID записей:")
        for i, entry_id in enumerate(dataset.get_all_ids()[:5]):
            print(f"  {i + 1}: {entry_id}")

        # Покажем первую запись для проверки
        first_id = dataset.get_all_ids()[0]
        first_exemplar = dataset.get_exemplar_by_id(first_id)
        print(f"\nПервая запись {first_id}:")
        print(f"  Сигнал: {len(first_exemplar.signal.signal_mv)} точек")
        print(f"  Точки: {list(first_exemplar._points.keys())}")

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.db.db_manager import DBManager
from CORE.db.forms_services import FormService
from CORE.db_dataclasses import Form
import random
import os
from typing import Optional, List

from CORE.datasets_wrappers import LUDB
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.db_dataclasses import Form
from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.run.r_form import RForm
from CORE.visual_debug import TrackRes, StepRes
from DA3.settings import Settings
from CORE.logger import get_logger

logger = get_logger(__name__)


class Simulator:
    def __init__(self):
        self.rform: Optional[RForm] = None
        self.settings = Settings()
        self.dataset: Optional[ExemplarsDataset] = None
        self._current_idx: int = -1
        self._exemplar_ids: List[str] = []

        self.ludb = LUDB()

    def _request_random_center_for_first_point(self, exemplar: Exemplar) -> Optional[float]:
        if not self.rform or not self.rform.form.points:
            return None
        first_point_name = self.rform.form.points[0].name
        real_coord = exemplar.get_point_coord(point_name=first_point_name)
        if real_coord is None:
            logger.warning(f"Точка {first_point_name} не найдена в exemplar")
            return None
        left_border = real_coord - self.settings.max_half_padding_from_real_coord_of_first
        right_border = real_coord + self.settings.max_half_padding_from_real_coord_of_first
        return random.uniform(left_border, right_border)

    def reset_form(self, form: Form):
        self.reset_dataset(dataset_name=form.path_to_dataset)

        parametrised_for_evaluator = ParametrisedDataset(form=form, raw_exemplars=self.dataset)
        evaluator_class = self.settings.evaluator_class

        # Пытаемся создать с параметром, если не получается - создаем без
        try:
            evaluator = evaluator_class(positive_dataset=parametrised_for_evaluator)
        except TypeError:
            # Если класс не принимает такой параметр, создаем без него
            evaluator = evaluator_class()
        self.rform = RForm(form, evaluator=evaluator)



    def reset_dataset(self, dataset_name: str) -> None:
        """dataset_name - имя файла датасета (без пути)"""
        if self.dataset is None or self.dataset.form_dataset_name != dataset_name:
            logger.info(f"Загрузка датасета: {dataset_name}")
            self.dataset = ExemplarsDataset(form_dataset_name=dataset_name, outer_dataset=self.ludb)
            self._exemplar_ids = self.dataset.get_all_ids()
            self._current_idx = -1
            logger.info(f"Загружено {len(self._exemplar_ids)} записей")

    def next(self) -> Optional[Exemplar]:
        """Переключиться на следующий экземпляр и вернуть его"""
        if not self.dataset or not self._exemplar_ids:
            return None

        next_idx = self._current_idx + 1
        if next_idx >= len(self._exemplar_ids):
            return None

        self._current_idx = next_idx
        return self.dataset.get_exemplar_by_id(self._exemplar_ids[self._current_idx])

    def prev(self) -> Optional[Exemplar]:
        """Переключиться на предыдущий экземпляр и вернуть его"""
        if not self.dataset or not self._exemplar_ids or self._current_idx <= 0:
            return None

        self._current_idx -= 1
        return self.dataset.get_exemplar_by_id(self._exemplar_ids[self._current_idx])

    def run_track(self, exemplar: Exemplar, track_id: int, form: Form) -> TrackRes:
        pass

    def run_step(self, exemplar: Exemplar, step_id: int, form: Form) -> StepRes:
        pass

    def run_form(self, exemplar: Exemplar, form: Form) -> ExemplarsPool:
        pass


if __name__ == "__main__":
    from CORE.paths import EXEMPLARS_DATASETS_PATH, DB_PATH
    import os

    # Проверим, какие файлы есть в директории
    print(f"Путь к датасетам: {EXEMPLARS_DATASETS_PATH}")
    if os.path.exists(EXEMPLARS_DATASETS_PATH):
        files = os.listdir(EXEMPLARS_DATASETS_PATH)
        print(f"Файлы в директории: {files}")

    # Загрузим тестовую форму
    db_manager = DBManager(DB_PATH)

    form_service = FormService()
    with db_manager.get_connection() as conn:
        test_form = form_service.get_form_by_id(form_id=1, conn=conn)

    sim = Simulator()
    sim.reset_form(test_form)

    print(f"\nЗагружен датасет qrs.json. Всего записей: {len(sim._exemplar_ids)}")

    if sim._exemplar_ids:
        print(f"Первые 5 ID записей: {sim._exemplar_ids[:5]}")

        # Проходим вперед по всем записям
        print("\nПроход вперед:")
        count = 0
        while True:
            ex = sim.next()
            if not ex:
                break
            print(f"  {count + 1}: {sim._exemplar_ids[sim._current_idx]}")
            count += 1

        print(f"\nВсего пройдено вперед: {count}")

        # Проходим назад по всем записям
        print("\nПроход назад:")
        count = 0
        while True:
            ex = sim.prev()
            if not ex:
                break
            print(f"  {count + 1}: {sim._exemplar_ids[sim._current_idx]}")
            count += 1

        print(f"\nВсего пройдено назад: {count}")
    else:
        print("Датасет qrs.json пуст!")

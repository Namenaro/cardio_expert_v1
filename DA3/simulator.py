import random
from typing import Optional, List, Union

from CORE.datasets_wrappers import LUDB
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.db.db_manager import DBManager
from CORE.db.forms_services import FormService
from CORE.db_dataclasses import Form
from CORE.logger import get_logger
from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.run.r_form import RForm
from CORE.visual_debug import TrackRes, StepRes
from DA3.settings import Settings
from DA3.simulator_utils import find_track, make_interval, get_coords, exec_track

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
        first = self.rform.form.points[0].name
        coord = exemplar.get_point_coord(point_name=first)
        if coord is None:
            logger.warning(f"Точка {first} не найдена")
            return None
        delta = self.settings.max_half_padding_from_real_coord_of_first
        return random.uniform(coord - delta, coord + delta)

    def reset_form(self, form: Form):
        self.reset_dataset(name=form.path_to_dataset)
        dataset = ParametrisedDataset(form=form, raw_exemplars=self.dataset)
        try:
            evaluator = self.settings.evaluator_class(positive_dataset=dataset)
        except TypeError:
            evaluator = self.settings.evaluator_class()
        self.rform = RForm(form, evaluator=evaluator)

    def reset_dataset(self, name: str) -> None:
        if self.dataset is None or self.dataset.form_dataset_name != name:
            logger.info(f"Загрузка датасета: {name}")
            self.dataset = ExemplarsDataset(form_dataset_name=name, outer_dataset=self.ludb)
            self._exemplar_ids = self.dataset.get_all_ids()
            self._current_idx = -1
            logger.info(f"Загружено {len(self._exemplar_ids)} записей")

    def next(self) -> Optional[Exemplar]:
        if not self.dataset or self._current_idx + 1 >= len(self._exemplar_ids):
            return None
        self._current_idx += 1
        return self.dataset.get_exemplar_by_id(self._exemplar_ids[self._current_idx])

    def prev(self) -> Optional[Exemplar]:
        if not self.dataset or self._current_idx <= 0:
            return None
        self._current_idx -= 1
        return self.dataset.get_exemplar_by_id(self._exemplar_ids[self._current_idx])

    def run_track(self, ex: Exemplar, track_id: int, form: Form, center: Optional[float] = None) -> Union[
        str, TrackRes]:
        if not self.rform:
            return "Форма не инициализирована"

        track_step = find_track(form, track_id)
        if not track_step:
            return f"Трек {track_id} не найден"

        track, step = track_step

        interval = make_interval(step)
        if isinstance(interval, str):
            return interval

        if step.num_in_form == 0:
            center = center or self._request_random_center_for_first_point(ex)
            if center is None:
                return "Нет центра для первого шага"

        coords = get_coords(interval, ex, center)
        if isinstance(coords, str):
            return coords

        left, right = coords
        signal = ex.get_signal()

        return exec_track(track, signal, left, right, track_id)

    def run_step(self, ex: Exemplar, step_id: int, form: Form) -> StepRes:
        pass

    def run_form(self, ex: Exemplar, form: Form) -> ExemplarsPool:
        pass


if __name__ == "__main__":
    from CORE.paths import EXEMPLARS_DATASETS_PATH, DB_PATH
    import os

    print(f"Датасеты: {EXEMPLARS_DATASETS_PATH}")
    if os.path.exists(EXEMPLARS_DATASETS_PATH):
        print(f"Файлы: {os.listdir(EXEMPLARS_DATASETS_PATH)}")

    db = DBManager(DB_PATH)
    forms = FormService()

    with db.get_connection() as conn:
        form = forms.get_form_by_id(form_id=1, conn=conn)

    print(f"\nФорма: {form.name}, шагов: {len(form.steps)}")

    sim = Simulator()
    sim.reset_form(form)

    if sim._exemplar_ids:
        ex = sim.next()
        if ex and form.steps and form.steps[0].tracks:
            tid = form.steps[0].tracks[0].id
            print(f"\nЗапуск трека {tid}:")

            # Тестируем только один раз, например с center=None
            print(f"\n  без центра:")
            res = sim.run_track(ex, tid, form, None)

            if isinstance(res, str):
                print(f"    → {res}")
            else:
                pts = res.to_uniq_coords()
                print(f"    → SM:{len(res.sm_res_objs)} PS:{len(res.ps_res_objs)} точек:{len(pts)}")
                if pts:
                    print(f"      {[f'{p:.3f}' for p in pts[:3]]}")

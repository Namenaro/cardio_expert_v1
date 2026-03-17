import random
from typing import Optional

from CORE.datasets_wrappers import LUDB
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.db_dataclasses import Form
from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug import TrackRes, StepRes
from DA3.settings import Settings


class Simulator:
    def __init__(self):
        self.form: Optional[Form] = None
        self.settings = Settings()
        self.dataset: Optional[ExemplarsDataset] = None

        self.ludb = LUDB()  # TODO потом еще птб хл

    def _request_random_center_for_first_point(self, exemplar: Exemplar) -> Optional[float]:
        if not self.form or not self.form.points:
            return None
        first_point_name = self.form.points[0].name
        real_coord = exemplar.get_point_coord(point_name=first_point_name)
        left_border = real_coord - self.settings.max_half_padding_from_real_coord_of_first
        right_border = real_coord + self.settings.max_half_padding_from_real_coord_of_first
        random_center = random.uniform(left_border, right_border)
        return random_center

    def reset_form(self, form: Form):
        self.form = form
        self.reset_dataset(dataset_name=form.path_to_dataset)

    def reset_dataset(self, dataset_name) -> None:
        """ Перезагружает датасет из файла только если нужно (если датасет с таким именем уже загружен, то ничего не делает) """
        if self.dataset is None or self.dataset.form_dataset_name != dataset_name:
            self.dataset = ExemplarsDataset(form_dataset_name=dataset_name, outer_dataset=self.ludb)

    def request_next_exemplar(self) -> Optional[Exemplar]:
        pass

    def request_prev_exemplar(self) -> Optional[Exemplar]:
        pass

    def run_track(self, exemplar: Exemplar, track_id: int, form: Form) -> TrackRes:
        pass

    def run_step(self, exemplar: Exemplar, step_id: int, form: Form) -> StepRes:
        pass

    def run_form(self, exemplar: Exemplar, form: Form) -> ExemplarsPool:
        pass

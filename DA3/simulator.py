from typing import Optional, List

from CORE import Signal
from CORE.datasets_wrappers import LUDB
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.db_dataclasses import BasePazzle, Track, Form
from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.visual_debug import TrackRes, StepRes


class Simulator:
    def __init__(self, half_padding_from_first_point: float):
        self.half_padding_from_first_point = half_padding_from_first_point
        self.dataset: Optional[ExemplarsDataset] = None

        self.ludb = LUDB()  # TODO потом еще птб хл

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

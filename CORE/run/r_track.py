from typing import List

from CORE.db_dataclasses import Track
from CORE.pazzles_lib.ps_base import PSBase
from CORE.pazzles_lib.sm_base import SMBase
from CORE.run import Exemplar
from CORE.run.step_interval import Interval
from CORE.run.utils import delete_simialr_points


class RTrack:
    def __init__(self, track: Track):
        self.id: int = track.id

        self.rSM_objects: List[SMBase] = []
        self.rPS_objects: List[PSBase] = []

    def run(self, exemplar: Exemplar, interval: Interval) -> List[float]:
        # 1. Запускаем SM-объекты в том  порядке, в каком они идут в списке и получаем измененный сигнал
        # убедитмся, что длина сигнала не изменилась после модификации, иначе исключение
        # 2. Запускаем PS-объекты на измененном сигнале
        # 3. Прореживаем дубли среди итоговых точек
        delete_simialr_points()

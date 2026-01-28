from dataclasses import dataclass
from typing import Optional, List

from CORE.run import Exemplar
from CORE.run.r_pc import R_PC
from CORE.run.r_track import RTrack
from CORE.run.step_interval import Interval
from CORE.run.utils import delete_simialr_points


class RStep:
    def __init__(self, interval: Interval, target_point_name: str):

        self.interval: Interval = interval
        self.target_point_name: str = target_point_name

        self.rHC_objects = []
        self.rPC_objects: List[R_PC] = []

        self.r_tracks: List[RTrack] = []

    def run(self, exemplar: Exemplar) -> List[Exemplar]:
        # 1. Зпускаем по очереди все треки и формируем список точек
        # 2. Прореживаем список точек, удяляя дубли
        # 3. На основе списка точек создаем дочерние экземпляры
        # 4. Параметризуем их
        # 5. Удялаяем те, которые нарушили жесткие условия на параметры
        delete_simialr_points()

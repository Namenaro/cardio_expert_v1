from dataclasses import dataclass
from typing import Optional, List

from CORE.run import Exemplar
from CORE.run.r_track import RTrack
from CORE.run.step_interval import Interval


class RStep:
    def __init__(self, interval: Interval, target_point_name):
        self.interval: Interval = interval

        self.rHC_objects = []
        self.rPC_objects = []

        self.target_point_name: str = target_point_name

        self.r_tracks: List[RTrack] = []

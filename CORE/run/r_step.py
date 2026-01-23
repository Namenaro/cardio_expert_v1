from dataclasses import dataclass
from typing import Optional

from CORE.run import Exemplar


class Interval:
    def __init__(self):
        self.left_point_name: Optional[str] = None
        self.left_padding: Optional[float] = None

        self.right_point_name: Optional[str] = None
        self.right_padding: Optional[float] = None

    def set_point_left(self, point_name: str) -> None:
        pass

    def set_point_right(self, point_name: str) -> None:
        pass

    def set_right_padding(self, dt: float) -> None:
        pass

    def set_left_padding(self, dt: float) -> None:
        pass

    def get_interval_coords(self, exemplar: Exemplar, center: Optional = None) -> (float, float):
        pass

    def validate(self) -> bool:
        pass

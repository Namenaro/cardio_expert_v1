from CORE.main_entities.track import Track
from CORE.main_entities.point import Point
from CORE.pazzles_lib.PC_base import PC
from CORE.pazzles_lib.HC_base import HC

from typing import Optional, List

class Step:
    def __init__(self):
        # Имя точки, ради которой затеян этот шаг установки
        self.target_point: Point = None

        # Список параллельных генераторов кандидатов
        self.tracks: List[Track] = []

        # Точки-ограничители интервала поиска, если они заданы
        self.right_point: Optional[Point] = None
        self.left_point: Optional[Point] = None

        # Первые в очереди установки точки и граничные точки
        # не имеют именованных точек-ограничителей интервала поиска
        self.left_padding: Optional[float] = None
        self.right_padding: Optional[float] = None

        # измерители параметров
        self.PCs: List[PC] = []

        # проверяльщики жестких условий на параметры
        self.HCs: List[HC] = []

        self.comment: str = ""



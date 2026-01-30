from CORE.db_dataclasses.track import Track
from CORE.db_dataclasses.point import Point

from typing import Optional, List, Set
from dataclasses import dataclass, field

@dataclass
class Step:
    # Порядковый номер шага в форме
    num_in_form: int

    # Имя точки, ради которой затеян этот шаг установки
    target_point: Optional[Point] = None  # Может быть NULL

    id: Optional[int] = None  # первичный ключ в таблице step

    # Список параллельных генераторов кандидатов
    tracks: List[Track] = field(default_factory=list)

    # Границы интервала, в котором надо поставить целевую точку
    right_point: Optional[Point] = field(default=None)  # Может быть NULL
    left_point: Optional[Point] = field(default=None)   # Может быть NULL
    left_padding_t: Optional[float] = None
    right_padding_t: Optional[float] = None

    comment: str = ""






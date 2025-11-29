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


    def is_valid(self) -> bool:
        """
        Валидация шага:
        1) Каждый трек должен быть валидным
        2) Должен быть хотя бы один трек
        3) Слева должно быть задано либо left_point, либо left_padding, но не оба
        4) Справа должно быть задано либо right_point, либо right_padding, но не оба
        """
        # 1) Проверка треков
        tracks_valid = all(track.is_valid() for track in self.tracks)
        has_tracks = len(self.tracks) > 0

        # 2) Проверка ограничения слева (XOR - либо одно, либо другое, но не оба)
        left_constraint_valid = (self.left_point is not None) != (self.left_padding_t is not None)

        # 3) Проверка ограничения справа (XOR - либо одно, либо другое, но не оба)
        right_constraint_valid = (self.right_point is not None) != (self.right_padding_t is not None)

        return all([
            tracks_valid,
            has_tracks,
            left_constraint_valid,
            right_constraint_valid
        ])







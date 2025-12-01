from CORE.db_dataclasses.base_pazzle import BasePazzle

from typing import List
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Track:
    """
    Генератор одного пула кандадатов на точку. Имеет структуру SM, ...,SM, PS,....PS.
    Модификаторов сигнала может не быть, но хоть один PS быть обязан.
    """
    id: Optional[int] = None

    SMs: List[BasePazzle] = field(default_factory=list)  # порядок важен
    PSs: List[BasePazzle] = field(default_factory=list) # порядок не важен

    def insert_sm(self, sm:BasePazzle, num_in_track:int):
        """Вставляет sm в позицию num_in_track с проверкой границ"""
        if num_in_track < 0:
            num_in_track = 0
        elif num_in_track > len(self.SMs):
            num_in_track = len(self.SMs)  # вставка в конец, если индекс слишком большой

        self.SMs.insert(num_in_track, sm)
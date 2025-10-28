from CORE.dataclasses.pazzles.object import SM_Object, PS_Object

from typing import List
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Track:
    """
    Генератор одного пула кандадатов на точку. Имеет структуру SM, ...,SM, PS,....PS.
    Модификаторов сигнала может не быть, но хоть один PS быть обязан.
    """
    id: Optional[int] = None  # первичный ключ в таблице parameter

    SMs: List[SM_Object] = field(default_factory=list)
    PSs: List[PS_Object] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.PSs) > 0

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

    SMs: List[BasePazzle] = field(default_factory=list)
    PSs: List[BasePazzle] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.PSs) > 0

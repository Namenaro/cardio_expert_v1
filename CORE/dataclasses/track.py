from CORE.dataclasses.pazzles.SM_PC_HC_PS import SM_ObjectEntry, PS_ObjectEntry

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

    SMs: List[SM_ObjectEntry] = field(default_factory=list)
    PSs: List[PS_ObjectEntry] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.PSs) > 0

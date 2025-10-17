from CORE.dataclasses.SM_PC_HC_PS import SM_ObjectEntry, PS_ObjectEntry

from typing import List
from dataclasses import dataclass, field


@dataclass
class Track:
    """
    Генератор одного пула кандадатов на точку. Имеет структуру SM, ...,SM, PS,....PS.
    Модификаторов сигнала может не быть, но хоть один PS быть обязан.
    """
    SMs: List[SM_ObjectEntry] = field(default_factory=list)
    PSs: List[PS_ObjectEntry] = field(default_factory=list)

    def is_valid(self) -> bool:
        return len(self.PSs) > 0

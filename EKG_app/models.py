from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Entry:
    """
    Хранит метаданные и ТЕКУЩУЮ РАЗМЕЧАЕМУЮ группу точек.
    """
    patient_id: str
    lead_name: str
    points: Dict[str, float] = field(default_factory=dict)
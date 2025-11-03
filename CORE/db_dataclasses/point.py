from dataclasses import dataclass

from typing import Optional

@dataclass
class Point:
        id: Optional[int] = None  # первичный ключ в таблице point
        name: str  = ""
        comment: str = ""
from dataclasses import dataclass

from typing import Optional

@dataclass
class Parameter:
        id: Optional[int] = None  # первичный ключ в таблице parameter
        name: str = ""
        comment: str = ""
        data_type: str = ""

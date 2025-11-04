from CORE.db_dataclasses.classes_to_pazzles_helpers import *

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from enum import Enum


class CLASS_TYPES(Enum):
    PC = "PC"
    HC = "HC"
    PS = "PS"
    SM = "SM"

@dataclass
class BaseClass:
    """
    Базовый класс на основе таблицы 'class' и 4 связанных с ней таблииц, дающих вместе полную сигнатуру любого класса пазла
    """
    id: Optional[int] = None
    name: str = ""  # NOT NULL UNIQUE
    comment: str = ""
    type: str = ""  # TYPE TEXT - одно из значений CLASS_TYPES

    # Связи с другими таблицами (опционально, для удобства)
    constructor_arguments: List[ClassArgument] = field(default_factory=list)  # названия аргументов конструктора, как если из docstring
    input_params: List[ClassInputParam] = field(default_factory=list)  # названия параметров с входа метода run, как если из docstring
    input_points: List[ClassInputPoint] = field(default_factory=list)  # названия точек с входа метода run, как если из docstring
    output_params: List[ClassOutputParam] = field(default_factory=list)  # названия параметров, возвращаемых методом run
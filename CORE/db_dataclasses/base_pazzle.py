from CORE.db_dataclasses.classes_to_pazzles_helpers import *
from CORE.db_dataclasses.base_class import BaseClass

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class BasePazzle:
    """
    Базовый объект на основе таблицы 'object'

    """
    id: Optional[int] = None
    name: Optional[str] = None      # Может быть NULL
    comment: str = ""

    # Ссылка на класс
    class_ref: Optional[BaseClass] = None

    # Связи с другими таблицами
    argument_values: List[ObjectArgumentValue] = field(default_factory=list)      # value_to_argument
    input_param_values: List[ObjectInputParamValue] = field(default_factory=list) # value_to_input_param
    input_point_values: List[ObjectInputPointValue] = field(default_factory=list) # value_to_input_point
    output_param_values: List[ObjectOutputParamValue] = field(default_factory=list) # value_to_output_param

    def is_HC(self)->bool:
        return self.class_ref.is_HC()
from CORE.db_dataclasses.classes_to_pazzles_helpers import *

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any





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

    def __repr__(self):
        lines = []
        lines.append(f"Class: {self.name} ({self.type})")
        if self.comment:
            lines.append(f"Description: {self.comment}")

        if self.constructor_arguments:
            lines.append("Constructor:")
            for arg in self.constructor_arguments:
                lines.append(f"  - {arg}")

        if self.input_points:
            lines.append("Input Points:")
            for point in self.input_points:
                lines.append(f"  - {point}")

        if self.input_params:
            lines.append("Input Parameters:")
            for param in self.input_params:
                lines.append(f"  - {param}")

        if self.output_params:
            lines.append("Output Parameters:")
            for param in self.output_params:
                lines.append(f"  - {param}")

        return "\n".join(lines)
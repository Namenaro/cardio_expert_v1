from typing import List, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum

#--------------------------------------------------
#  Аргументы конструктора для любого пазла
#--------------------------------------------------
# в БД в поле class.TYPE могут быть только строки:
class DATA_TYPES(Enum):
    INT = "int"
    FLOAT = "float"
    STR = "str"
    BOOL = "bool"

# Для таблицы argument_to_class
@dataclass
class ClassArgument:
    """Аргумент конструктора класса"""
    id: Optional[int] = None
    class_id: Optional[int] = None
    name: str = ""  # NOT NULL
    comment: str = ""
    data_type: str = ""  # NOT NULL см. DATA_TYPES
    default_value: Optional[str] = None

    def __repr__(self):
        default_str = f" = {self.default_value}" if self.default_value else ""
        comment_str = f"  # {self.comment}" if self.comment else ""
        return f"{self.name}: {self.data_type}{default_str}{comment_str}"


# Для таблицы value_to_argument
@dataclass
class ObjectArgumentValue:
    """Значение аргумента для объекта """
    id: Optional[int] = None
    object_id: Optional[int] = None
    argument_id: Optional[int] = None
    argument_value: str = ""

#--------------------------------------------------
#  Входящие параметры для метода run (это нужно только пазлам типа PC и HC)
#--------------------------------------------------
@dataclass
class ClassInputParam:
    """Входной параметр класса"""
    id: Optional[int] = None
    class_id: Optional[int] = None
    name: str = ""  # NOT NULL
    comment: str = ""
    data_type: str = ""  # NOT NULL см. DATA_TYPES

    def __repr__(self):
        comment_str = f"  # {self.comment}" if self.comment else ""
        return f"{self.name}: {self.data_type}{comment_str}"

@dataclass
class ObjectInputParamValue:
    """Значение входного параметра для объекта"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    input_param_id: Optional[int] = None
    parameter_id: Optional[int] = None  # Ссылка на parameter.id

#--------------------------------------------------
#  Исходящие параметры для метода run (это нужно только пазлам типа PC)
#--------------------------------------------------
@dataclass
class ClassOutputParam:
    """Выходной параметр класса"""
    id: Optional[int] = None
    class_id: Optional[int] = None
    name: str = ""  # NOT NULL
    comment: str = ""
    data_type: str = ""  # NOT NULL см. DATA_TYPES

    def __repr__(self):
        comment_str = f"  # {self.comment}" if self.comment else ""
        return f"{self.name}: {self.data_type}{comment_str}"


@dataclass
class ObjectOutputParamValue:
    """Значение выходного параметра для объекта"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    output_param_id: Optional[int] = None
    parameter_id: Optional[int] = None  # Ссылка на parameter.id

#--------------------------------------------------
#  Входящие точки для метода run (это нужно только пазлам типа PC)
#--------------------------------------------------
@dataclass
class ClassInputPoint:
    """Входная точка класса"""
    id: Optional[int] = None
    class_id: Optional[int] = None
    name: str = ""  # NOT NULL
    comment: str = ""

    def __repr__(self):
        comment_str = f"  # {self.comment}" if self.comment else ""
        return f"{self.name}{comment_str}"

@dataclass
class ObjectInputPointValue:
    """Значение входной точки для объекта"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    input_point_id: Optional[int] = None
    point_id: Optional[int] = None  # Ссылка на point.id

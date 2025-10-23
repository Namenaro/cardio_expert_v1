from typing import List, Optional, Dict
from dataclasses import dataclass, field

from enum import Enum


class TYPES(Enum):
    PC = "PC"
    HC = "HC"
    PS = "PS"
    SM = "SM"


# в БД в поле class.TYPE могут быть только строки:
class DATA_TYPES(Enum):
    INT = "int"
    FLOAT = "float"
    STR = "str"
    BOOL = "bool"


@dataclass
class Class:
    id: Optional[int] = None  # первичный ключ в такблице class
    name: str = ""
    comment: str = ""

    # Спецификация аргументов конструктора класса, все брать из таблицы
    # argument_to_class по внешнему ключу к class.id
    args_ids_to_names: Dict[int, str] = field(default_factory=dict)
    args_ids_to_defaults: Dict[int, str] = field(default_factory=dict)
    ars_ids_to_comments: Dict[int, str] = field(default_factory=dict)
    ars_ids_to_datatypes: Dict[int, str] = field(default_factory=dict)


@dataclass
class SM_Class(Class):
    metainfo: str = ("Signal Modificator: Все классы этого типа получают на вход сигнал "
                     "и возвращают сигнал той же длины")


@dataclass
class PS_Class(Class):
    metainfo: str = ("Point Selector: Все классы этого типа получают на вход сигнал "
                     "и возвращают список координат_t выбранных особых точек")


@dataclass
class HC_Class(Class):
    metainfo: str = ("Hard Condition: Все классы этого типа получают на "
                     "вход набор параметров, а возвращают True\False")

    # Входные параметры формы для метода run,  брать из
    # таблицы input_param_to_class (по внешнему ключу к class.id)
    params_ids_to_names: Dict[int, str] = field(default_factory=dict)
    params_ids_to_comments: Dict[int, str] = field(default_factory=dict)


@dataclass
class PC_Class(Class):
    metainfo: str = ("Parameters Calculator: Все классы этого типа получают на "
                     "вход набор параметров и координаты уже поставленных на сигнале"
                     " точек этой формы, а возвращают результат расчета новых параметров"
                     " в виде словаря")

    # Входные параметры формы для метода run (params, points),  брать из
    # таблицы input_param_to_class (по внешнему ключу к class.id)
    params_ids_to_names: Dict[int, str] = field(default_factory=dict)
    params_ids_to_comments: Dict[int, str] = field(default_factory=dict)

    # Входные точки формы для метода run (params, points),  брать из
    # таблицы input_point_to_class (по внешнему ключу к class.id)
    point_ids_to_names: Dict[int, str] = field(default_factory=dict)
    point_ids_to_comments: Dict[int, str] = field(default_factory=dict)

    # Выходные параметры из метода run (params, points),  брать из
    # таблицы output_param_to_class (по внешнему ключу к class.id)
    OUT_params_ids_to_names: Dict[int, str] = field(default_factory=dict)
    OUT_params_ids_to_comments: Dict[int, str] = field(default_factory=dict)

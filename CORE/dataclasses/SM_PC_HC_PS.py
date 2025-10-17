from dataclasses import dataclass, field
from typing import Any, Dict

# Вспомогательные классы-------------------------------------
@dataclass
class ClassInfo:
    class_name: str
    class_comment: str
    class_type: str #PC, HC, ...

    args_names_to_types: Dict[str, str]
    args_names_to_default_vals: Dict[str, Any]
    args_names_to_comments: Dict[str, str]

    def add_constructor_arg(self, arg_name, default_val, data_type, arg_comment):
        self.args_names_to_types[arg_name]=data_type
        self.args_names_to_default_vals[arg_name] = default_val
        self.args_names_to_comments[arg_name] = arg_comment


# --------------------------------------------------------------------------
# Основные 4 класса: каждый объект любого из них содержит всю
# информацию для конструирования объекта соотв.типа и запуска его метода run.
# --------------------------------------------------------------------------
""" Модификация сигнала """
@dataclass
class SM_ObjectEntry:
    class_info: ClassInfo
    object_name: ""
    object_comment: str = ""

    # для вызова конструктора
    argname_to_argval: Dict[str, Any] = field(default_factory=dict)

    """ Селектор пула точек на сигнале """
@dataclass
class PS_ObjectEntry:
    class_info: ClassInfo
    object_name: ""
    object_comment: str = ""

    # для вызова конструктора
    argname_to_argval: Dict[str, Any] = field(default_factory=dict)


""" Правило замера параметра(-ов) по набору поставленных точек и набору уже померенных параметров """
@dataclass
class PC_ObjectEntry:
    class_info: ClassInfo
    object_name: ""
    object_comment: str = ""

    # для вызова конструктора
    argname_to_argval: Dict[str, Any] = field(default_factory=dict)

    # для вызова run
    input_params: Dict[str, ParamInfo] = field(default_factory=dict)
    input_points_to_info: Dict[str, ParamInfo] = field(default_factory=dict)

    # какие параметры и их значения на выходе run
    output_params_to_info: Dict[str, ParamInfo] = field(default_factory=dict)


""" Жесткое условие поверх группы параметров """
@dataclass
class HC_ObjectEntry:
    class_info: ClassInfo

    object_name: ""
    object_comment: str = ""

    # для вызова конструктора
    argname_to_argval: Dict[str, Any] = field(default_factory=dict)

    # для вызова run
    input_params_to_info: Dict[str, ParamInfo] = field(default_factory=dict)










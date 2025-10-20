from dataclasses import dataclass, field
from typing import Any, Dict, Set

# ----------------------------------------------------------
# Классы, в которые сериализуются таблицы, описывающие только сигнатуры классов 4 типов (т.е. как коассы назваются, что ожидают их конструкторы)
@dataclass
class InputArgsInfo:
    args_names_to_types: Dict[str, str] = field(default_factory=dict)
    args_names_to_default_vals: Dict[str, Any]  = field(default_factory=dict)
    args_names_to_comments: Dict[str, str] = field(default_factory=dict)


    def add_arg(self, arg_name:str, default_val:Any, data_type:str, arg_comment:str=""):
        self.args_names_to_types[arg_name] = data_type
        self.args_names_to_default_vals[arg_name] = default_val
        self.args_names_to_comments[arg_name] = arg_comment

@dataclass
class InputPointsInfo:
    points_names_to_comments: Dict[str, str] = field(default_factory=dict)

    def add_point(self, point_name:str, comment:str=""):
        self.points_names_to_comments[point_name] = comment


@dataclass
class ParamsInfo:
    params_names_to_comments: Dict[str, str] = field(default_factory=dict)

    def add_param(self, param_name: str, comment: str=""):
        self.params_names_to_comments[param_name] = comment


""" Модификация сигнала """
@dataclass
class SMClassInfo:
    class_name: str
    class_comment: str

    input_args_info: InputArgsInfo

""" Селектор пула точек на сигнале """
@dataclass
class PSClassInfo:
    class_name: str
    class_comment: str

    input_args_info: InputArgsInfo

""" Правило замера параметра(-ов) по набору поставленных точек и набору уже померенных параметров """
@dataclass
class PCClassInfo:
    class_name: str
    class_comment: str

    input_args_info: InputArgsInfo
    input_params_info: ParamsInfo
    input_points_info: InputPointsInfo

    output_params_info: ParamsInfo

""" Жесткое условие поверх группы параметров """
@dataclass
class HCClassInfo:
    class_name: str
    class_comment: str

    input_args_info: InputArgsInfo
    input_params_info: ParamsInfo

# --------------------------------------------------------------------------
# Классы, в которые сериализуются таблицы, описывающие создание уже конкретных объектов классов 4 типов
""" Модификация сигнала """
@dataclass
class SM_ObjectEntry:
    class_info: SMClassInfo
    object_name: str
    object_comment: str = ""

    args_names_to_vals: Dict[str, Any] = field(default_factory=dict)

    def add_arg_val(self, arg_name:str, arg_val:Any):
        self.args_names_to_vals[arg_name] = arg_val



""" Селектор пула точек на сигнале """
@dataclass
class PS_ObjectEntry:
    class_info: PSClassInfo
    object_name: ""
    object_comment: str = ""

    args_names_to_vals: Dict[str, Any] = field(default_factory=dict)

    def add_arg_val(self, arg_name: str, arg_val: Any):
        self.args_names_to_vals[arg_name] = arg_val


""" Правило замера параметра(-ов) по набору поставленных точек и набору уже померенных параметров """
@dataclass
class PC_ObjectEntry:
    class_info: PCClassInfo
    object_name: ""
    object_comment: str = ""

    args_names_to_vals: Dict[str, Any] = field(default_factory=dict)
    input_params_names_to_vals: Dict[str, str] = field(default_factory=dict)
    input_points_names_to_vals: Dict[str, str] = field(default_factory=dict)

    output_params_to_vals: Dict[str, str] = field(default_factory=dict)



""" Жесткое условие поверх группы параметров """
@dataclass
class HC_ObjectEntry:
    class_info: HCClassInfo

    object_name: ""
    object_comment: str = ""

    args_names_to_vals: Dict[str, Any] = field(default_factory=dict)
    input_params_names_to_vals: Dict[str, str] = field(default_factory=dict)










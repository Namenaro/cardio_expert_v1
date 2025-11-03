from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from CORE.db_dataclasses.pazzles.class_ import Class, PC_Class, SM_Class, HC_Class, PS_Class
from CORE.db_dataclasses.utils import map_names_to_values_throught_id
from CORE.db_dataclasses.point import Point
from CORE.db_dataclasses.parameter import Parameter


@dataclass
class Object:
    id: Optional[int] = None  # первичный ключ в такблице object
    name: str = ""
    comment: str = ""
    class_signature: Optional[Class] = None

    # значения аргументов коструктора
    args_ids_to_vals: Dict[int, Any] = field(default_factory=dict)


@dataclass
class SM_Object(Object):
    class_signature: Optional[SM_Class] = None


@dataclass
class PS_Object(Object):
    class_signature: Optional[PS_Class] = None


@dataclass
class HC_Object(Object):
    class_signature: Optional[HC_Class] = None

    # значения для входящих параметров:
    # {intput_param_id, parameter_id}
    # из тех строк таблицы value_to_input_param,
    # где object_id == self.id
    param_argids_to_parameters: Dict[int, Parameter] = field(default_factory=dict)

    def get_input_params_map(self) -> Dict[str, str]:
        """ Создаем словарь
        {имя параметра как аргумента метода run -
        имя параемтра как параметра формы},
        будем передавать его в run
        """
        param_argids_to_parameter_names = {
            param_id: parameter.name
            for param_id, parameter in self.param_argids_to_parameters.items()
        }
        argnames_to_names_in_form = map_names_to_values_throught_id(
            ids_to_names=self.class_signature.params_ids_to_names,
            ids_to_vals=param_argids_to_parameter_names)
        return argnames_to_names_in_form


@dataclass
class PC_Object(Object):
    class_signature: Optional[PC_Class] = None

    # значения для входящих параметров:
    # {intput_param_id, parameter_id}
    # из тех строк таблицы value_to_input_param,
    # где object_id == self.id
    param_argids_to_parameters: Dict[int, Parameter] = field(default_factory=dict)

    # значения для входящих точек:
    # {input_point_id, point_id}
    # из тех строк таблицы value_to_input_point,
    # где object_id == self.id
    points_argids_to_points: Dict[int, Point] = field(default_factory=dict)

    # значения для исходящих параметров
    # {output_param_id, parameter_id}
    # из тех строк таблицы value_to_output_point,
    # где object_id == self.id
    OUT_param_argids_to_parameters: Dict[int, Parameter] = field(default_factory=dict)

    def get_input_params_map(self)->Dict[str, str]:
        """ Создаем словарь
        {имя параметра как аргумента метода run -
        имя параемтра как параметра формы},
        будем передавать его в run
        """
        param_argids_to_parameter_names = {
            param_id: parameter.name
            for param_id, parameter in self.param_argids_to_parameters.items()
        }
        argnames_to_names_in_form = map_names_to_values_throught_id(
            ids_to_names=self.class_signature.params_ids_to_names,
            ids_to_vals=param_argids_to_parameter_names)
        return argnames_to_names_in_form

    def get_OUTput_params_map(self)->Dict[str, str]:
        """ Создаем словарь
        {имя параметра как ключа из возвращаемого словаря метода run -
        имя параемтра как параметра формы}
        """
        param_argids_to_parameter_names = {
            param_id: parameter.name
            for param_id, parameter in self.OUT_param_argids_to_parameters.items()
        }
        argnames_to_names_in_form = map_names_to_values_throught_id(
            ids_to_names=self.class_signature.OUT_params_ids_to_names,
            ids_to_vals=param_argids_to_parameter_names)
        return argnames_to_names_in_form

    def get_input_points_map(self)->Dict[str, str]:
        """ Создаем словарь
        {имя точки как аргумента метода run -
        имя точки как точки формы},
        будем передавать его в run
        """
        point_argids_to_point_names_in_form = {
            point_arg_id: point.name
            for point_arg_id, point in self.points_argids_to_points.items()
        }
        argnames_to_names_in_form = map_names_to_values_throught_id(
            ids_to_names=self.class_signature.point_ids_to_names,
            ids_to_vals=point_argids_to_point_names_in_form)
        return argnames_to_names_in_form



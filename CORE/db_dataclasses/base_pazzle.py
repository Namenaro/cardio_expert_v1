from CORE.db_dataclasses.classes_to_pazzles_helpers import *
from CORE.db_dataclasses.base_class import BaseClass

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Set


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

    def is_PC(self):
        return self.class_ref.is_PC()

    def is_SM(self):
        return self.class_ref.is_SM()

    def is_PS(self):
        return self.class_ref.is_PS()

    def get_args_names_to_vals(self) -> Dict[str, str]:
        """
        Возвращает словарь, где ключи - имена аргументов конструктора (ClassArgument.name),
        а значения - соответствующие значения аргументов (ObjectArgumentValue.argument_value).

        Сопоставление происходит через argument_id.

        Raises:
            ValueError: если набор ObjectArgumentValue не совпадает с ClassArgument
        """
        if self.class_ref is None:
            raise ValueError("BasePazzle не имеет ссылки на класс (class_ref is None)")

        # Создаем словарь для быстрого доступа к значениям по argument_id
        value_by_arg_id: Dict[int, str] = {}
        for arg_value in self.argument_values:
            if arg_value.argument_id is None:
                raise ValueError(f"ObjectArgumentValue с id={arg_value.id} не имеет argument_id")
            if arg_value.argument_id in value_by_arg_id:
                raise ValueError(f"Дублирование argument_id={arg_value.argument_id} в argument_values")
            value_by_arg_id[arg_value.argument_id] = arg_value.argument_value

        # Создаем словарь для быстрого доступа к именам аргументов по argument_id
        name_by_arg_id: Dict[int, str] = {}
        for class_arg in self.class_ref.constructor_arguments:
            if class_arg.id is None:
                raise ValueError(f"ClassArgument с name='{class_arg.name}' не имеет id")
            if class_arg.id in name_by_arg_id:
                raise ValueError(f"Дублирование id={class_arg.id} в constructor_arguments")
            name_by_arg_id[class_arg.id] = class_arg.name

        # Проверяем соответствие наборов
        if value_by_arg_id.keys() != name_by_arg_id.keys():
            raise ValueError("Множества argument_id не совпадают.")

        # Собираем итоговый словарь
        result: Dict[str, str] = {}
        for arg_id, arg_name in name_by_arg_id.items():
            result[arg_name] = value_by_arg_id[arg_id]

        return result

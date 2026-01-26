def _convert_value(self, value: str, target_type):
    """Преобразует строку в указанный тип"""
    if value is None:
        raise ValueError("Value cannot be None")
    if value == "":
        raise ValueError("Value cannot be empty string")

    # Обработка list[int] и list[float]
    origin = get_origin(target_type)
    if origin is list:
        args = get_args(target_type)
        if len(args) == 1:
            elem_type = args[0]
            # Удаляем скобки и разбиваем по запятым
            value = value.strip('[] ')
            if not value:
                raise ValueError("List cannot be empty")
            elements = [elem.strip() for elem in value.split(',') if elem.strip()]

            if elem_type == int:
                return [int(elem) for elem in elements]
            elif elem_type == float:
                return [float(elem) for elem in elements]

    # Базовые типы
    if target_type == bool:
        val_lower = value.lower()
        if val_lower == 'true':
            return True
        elif val_lower == 'false':
            return False
        else:
            raise ValueError(f"Bool must be 'true' or 'false', got: {value}")
    elif target_type == int:
        return int(value)
    elif target_type == float:
        return float(value)
    elif target_type == str:
        return str(value)

    raise ValueError(f"Unsupported type: {target_type}")


def create(self, classname: str, args: Dict[str, str]):
    """Создает объект класса с преобразованием типов аругментов из строки
     в ожидаемый сигнатурой коснтруктора тип"""

    if classname not in self._registry:
        raise ValueError(f"Class {classname} not found")

    cls = self._registry[classname]
    signature = inspect.signature(cls.__init__)
    type_hints = get_type_hints(cls.__init__)

    prepared_args = {}

    for param_name, param in signature.parameters.items():
        if param_name == 'self':
            continue

        if param_name in args:
            value = args[param_name]
            expected_type = type_hints.get(param_name, str)

            try:
                prepared_args[param_name] = self._convert_value(value, expected_type)
            except Exception as e:
                raise ValueError(
                    f"Не смогли конвертировать '{param_name}'='{value}' в {expected_type}: {e}"
                )
        elif param.default != inspect.Parameter.empty:
            prepared_args[param_name] = param.default
        else:
            raise ValueError(f"Отстуствует аргумент: {param_name}")

    return cls(**prepared_args)

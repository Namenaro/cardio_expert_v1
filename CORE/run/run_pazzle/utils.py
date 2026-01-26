import ast
from typing import Any, get_origin, get_args


def convert_value(value_str: str, target_type: type) -> Any:
    """
    Конвертирует строковое значение в указанный тип.
    Поддерживает: bool, float, int, str, list[float], list[int], list[str].
    Принимает списки в форматах:
      - "1,2,3"
      - "[1,2,3]"
    """
    try:
        if target_type is bool:
            return _str_to_bool(value_str)
        elif target_type is int:
            return int(float(value_str))
        elif target_type is float:
            return float(value_str)
        elif target_type is str:
            return value_str
        # Проверка на List[T]
        elif (hasattr(target_type, '__origin__') and
              get_origin(target_type) is list and
              len(get_args(target_type)) == 1):
            inner_type = get_args(target_type)[0]
            parsed_list = _parse_list_string(value_str)
            return [_convert_single_item(item, inner_type) for item in parsed_list]
        else:
            raise ValueError(f"Тип {target_type} не поддерживается")
    except Exception as e:
        raise ValueError(f"Ошибка конвертации '{value_str}' в {target_type}: {e}")


def _parse_list_string(value_str: str) -> list:
    """Парсит строку как список, поддерживая два формата: '1,2,3' и '[1,2,3]'."""
    value_str = value_str.strip()

    # Если строка начинается с [ и заканчивается на ], используем ast.literal_eval
    if value_str.startswith('[') and value_str.endswith(']'):
        try:
            result = ast.literal_eval(value_str)
            if not isinstance(result, list):
                raise ValueError("Значение не является списком")
            return result
        except (SyntaxError, ValueError) as e:
            raise ValueError(f"Не удалось парсить список: {e}")

    # Иначе разделяем по запятым
    else:
        return [item.strip() for item in value_str.split(',') if item.strip()]


def _str_to_bool(s: str) -> bool:
    s_clean = s.strip().lower()
    if s_clean in ('true', '1', 'yes'):
        return True
    if s_clean in ('false', '0', 'no'):
        return False
    raise ValueError(f"Не удаётся интерпретировать '{s}' как bool")


def _convert_single_item(item: Any, target_type: type) -> Any:
    if isinstance(item, target_type):
        return item
    if target_type is int:
        return int(float(item))  # '3.14' → 3
    if target_type is float:
        return float(item)
    if target_type is str:
        return str(item)
    raise ValueError(f"Невозможно конвертировать {item} в {target_type}")


if __name__ == "__main__":
    from typing import List

    print(f"int('42') = {convert_value('42', int)}")
    print(f"List[float]('1.1,2.2,3.3') = {convert_value('1.1,2.2,3.3', List[float])}")
    print(f"List[float]('[1.1,2.2,3.3]') = {convert_value('1.1,2.2,3.3', List[float])}")

import pytest
from typing import Any, get_type_hints, List, get_origin, get_args
from dataclasses import dataclass

from unittest.mock import patch

# Импорты из вашего проекта
from CORE.db_dataclasses import (
    BasePazzle, ClassInputPoint, ObjectInputPointValue, Point,
    Parameter, ClassInputParam, ObjectInputParamValue,
    ClassOutputParam, ObjectOutputParamValue, ClassArgument, ObjectArgumentValue
)
from CORE.run.run_pazzle.classes_registry import classes_registry
from CORE.run.run_pazzle.pazzle_parser import PazzleParser


# --- Вспомогательные классы ---


@dataclass
class DummyClass:
    """Класс с аннотированными типами для тестов."""
    x: float
    y: str
    flag: bool

    def __init__(self, x: float, y: str, flag: bool):
        self.x = x
        self.y = y
        self.flag = flag


@dataclass
class ListDummyClass:
    x: List[int]
    y: str

    def __init__(self, x: List[int], y: str):
        self.x = x
        self.y = y


# --- Фикстуры ---


@pytest.fixture
def setup_registry():
    """Регистрирует DummyClass в реестре."""
    classes_registry.register("DummyClass", DummyClass)
    return classes_registry


@pytest.fixture
def base_pazzle():
    """Базовый экземпляр BasePazzle с тестовыми данными."""
    return BasePazzle(
        class_ref=type("ClassRef", (), {
            "name": "DummyClass",
            "input_points": [
                ClassInputPoint(id=1, class_id=1, name="a"),
                ClassInputPoint(id=2, class_id=1, name="b"),
            ],
            "input_params": [
                ClassInputParam(id=10, class_id=1, name="p1"),
                ClassInputParam(id=11, class_id=1, name="p2"),
            ],
            "output_params": [
                ClassOutputParam(id=20, class_id=1, name="out1"),
                ClassOutputParam(id=21, class_id=1, name="out2"),
            ],
            "constructor_arguments": [
                ClassArgument(id=100, class_id=1, name="x", data_type="float"),
                ClassArgument(id=101, class_id=1, name="y", data_type="str"),
                ClassArgument(id=102, class_id=1, name="flag", data_type="bool"),
            ]
        })(),
        input_point_values=[
            ObjectInputPointValue(input_point_id=1, point_id=101),
            ObjectInputPointValue(input_point_id=2, point_id=102),
        ],
        input_param_values=[
            ObjectInputParamValue(input_param_id=10, parameter_id=201),
            ObjectInputParamValue(input_param_id=11, parameter_id=202),
        ],
        output_param_values=[
            ObjectOutputParamValue(output_param_id=20, parameter_id=301),
            ObjectOutputParamValue(output_param_id=21, parameter_id=302),
        ],
        argument_values=[
            ObjectArgumentValue(argument_id=100, argument_value="3.14"),
            ObjectArgumentValue(argument_id=101, argument_value="hello"),
            ObjectArgumentValue(argument_id=102, argument_value="true"),
        ]
    )


@pytest.fixture
def form_points():
    return [
        Point(id=101, name="point_A"),
        Point(id=102, name="point_B"),
    ]


@pytest.fixture
def form_params():
    return [
        Parameter(id=201, name="param_P1"),
        Parameter(id=202, name="param_P2"),
        Parameter(id=301, name="param_OUT1"),
        Parameter(id=302, name="param_OUT2"),
    ]


@pytest.fixture
def parser(base_pazzle, form_points, form_params, setup_registry):
    return PazzleParser(base_pazzle, form_points, form_params)


# --- Тесты ---

# 1. Тесты для map_point_names

def test_map_point_names(parser):
    result = parser.map_point_names()
    assert result == {"a": "point_A", "b": "point_B"}


def test_map_point_names_mismatch_count(parser, base_pazzle):
    base_pazzle.class_ref.input_points = base_pazzle.class_ref.input_points[:1]
    with pytest.raises(ValueError, match="Количество точек в классе.*не совпадает"):
        parser.map_point_names()


def test_map_point_names_duplicate_names(parser, base_pazzle):
    base_pazzle.class_ref.input_points[1].name = "a"
    with pytest.raises(ValueError, match="дублирующиеся имена точек"):
        parser.map_point_names()


# 2. Тесты для map_input_params_names

def test_map_input_params_names(parser):
    result = parser.map_input_params_names()
    assert result == {"p1": "param_P1", "p2": "param_P2"}


def test_map_input_params_names_missing(parser, base_pazzle):
    base_pazzle.input_param_values = []
    with pytest.raises(ValueError, match="не совпадает с полученными соответствиями"):
        parser.map_input_params_names()


# 3. Тесты для map_output_params_names


def test_map_output_params_names(parser):
    result = parser.map_output_params_names()
    assert result == {"out1": "param_OUT1", "out2": "param_OUT2"}


def test_map_output_params_names_missing_param(parser, form_params):
    form_params.pop()  # удаляем param_OUT2
    with pytest.raises(ValueError, match="Не найдено соответствующего параметра в форме"):
        parser.map_output_params_names()


# 4. Тесты для get_constructor_arguments


@pytest.mark.parametrize(
    ("arg_value_x, expected_x, arg_value_y, expected_y, arg_value_flag, expected_flag"),
    [
        ("3.14", 3.14, "hello", "hello", "true", True),
        ("42.0", 42.0, "world", "world", "false", False),
        ("0.5", 0.5, "test", "test", "True", True),  # регистронезависимость
        ("100.99", 100.99, "data", "data", "FALSE", False),  # регистронезависимость
    ])
def test_get_constructor_arguments_parametrized(
        arg_value_x: str,
        expected_x: float,
        arg_value_y: str,
        expected_y: str,
        arg_value_flag: str,
        expected_flag: bool,
        base_pazzle: BasePazzle,
        form_points: list[Point],
        form_params: list[Parameter],
        setup_registry
):
    """
    Проверяет конвертацию строковых значений в типы конструктора DummyClass.
    Требования:
    - Все аргументы обязательны (пустые строки не допускаются).
    - Для bool допустимы только "true"/"false" (без учёта регистра).
    """
    # Обновляем значения аргументов в base_pazzle
    base_pazzle.argument_values[0].argument_value = arg_value_x
    base_pazzle.argument_values[1].argument_value = arg_value_y
    base_pazzle.argument_values[2].argument_value = arg_value_flag.lower()  # нормализуем регистр

    parser = PazzleParser(base_pazzle, form_points, form_params)
    result = parser.get_constructor_arguments()

    # Проверяем все три аргумента
    assert result["x"] == expected_x
    assert result["y"] == expected_y
    assert result["flag"] is expected_flag


# 5. Тесты для крайних/особых случаев get_constructor_arguments


def test_get_constructor_arguments_invalid_float(base_pazzle, form_points, form_params, setup_registry):
    """Проверяет обработку невалидного float."""
    base_pazzle.argument_values[0].argument_value = "abc"
    parser = PazzleParser(base_pazzle, form_points, form_params)

    with pytest.raises(ValueError, match="Ошибка конвертации.*в <class 'float'>"):
        parser.get_constructor_arguments()


def test_get_constructor_arguments_invalid_bool(base_pazzle, form_points, form_params, setup_registry):
    """Проверяет обработку невалидного bool."""
    base_pazzle.argument_values[2].argument_value = "maybe"
    parser = PazzleParser(base_pazzle, form_points, form_params)

    with pytest.raises(ValueError, match="Не удаётся интерпретировать.*как bool"):
        parser.get_constructor_arguments()


def test_get_constructor_arguments_missing_argument(base_pazzle, form_points, form_params, setup_registry):
    """Проверяет отсутствие аргумента в base_pazzle."""
    # Удаляем один из аргументов
    base_pazzle.argument_values.pop(0)  # убираем аргумент для "x"

    parser = PazzleParser(base_pazzle, form_points, form_params)

    with pytest.raises(ValueError, match=r"^Нет значения для аргумента"):
        parser.get_constructor_arguments()


def test_get_constructor_arguments_type_hint_mismatch(
        base_pazzle, form_points, form_params, setup_registry
):
    # Ожидаемые подменённые аннотации
    mocked_annotations = {"x": int, "y": str, "flag": bool}

    # ПОДМЕНЯЕМ get_type_hints В МОДУЛЕ ПАРСЕРА
    with patch(
            "CORE.run.run_pazzle.pazzle_parser.get_type_hints",
            return_value=mocked_annotations
    ) as mock_get_type_hints:
        parser = PazzleParser(base_pazzle, form_points, form_params)
        result = parser.get_constructor_arguments()

        # Проверяем, что mock был вызван
        assert mock_get_type_hints.call_count == 1
        call_args, _ = mock_get_type_hints.call_args
        assert call_args[0].__name__ == "__init__"  # передали __init__

    # Проверяем результат конвертации
    assert result["x"] == 3  # "3.14" → int → 3
    assert isinstance(result["x"], int)  # тип точно int
    assert result["y"] == "hello"  # str без изменений
    assert result["flag"] is True  # bool без изменений


def test_get_constructor_arguments_list_int(
        base_pazzle, form_points, form_params, setup_registry
):
    # 1. Регистрируем класс
    classes_registry.register("ListDummyClass", ListDummyClass)

    # 2. Настраиваем base_pazzle
    base_pazzle.class_ref = type("ClassRef", (), {
        "name": "ListDummyClass",
        "input_points": [],
        "input_params": [],
        "output_params": [],
        "constructor_arguments": [
            ClassArgument(id=100, class_id=1, name="x", data_type="str"),
            ClassArgument(id=101, class_id=1, name="y", data_type="str"),
        ]
    })()

    base_pazzle.argument_values = [
        ObjectArgumentValue(argument_id=100, argument_value="1,2,3"),
        ObjectArgumentValue(argument_id=101, argument_value="hello"),
    ]

    # 3. Подменяем get_type_hints
    mocked_annotations = {"x": List[int], "y": str}

    with patch(
            "CORE.run.run_pazzle.pazzle_parser.get_type_hints",  # ← укажите верный путь!
            return_value=mocked_annotations
    ) as mock_get_type_hints:
        parser = PazzleParser(base_pazzle, form_points, form_params)
        result = parser.get_constructor_arguments()

        assert mock_get_type_hints.call_count == 1

    # 4. Проверки
    assert result["x"] == [1, 2, 3]
    assert isinstance(result["x"], list)
    assert all(isinstance(item, int) for item in result["x"])

    assert result["y"] == "hello"
    assert isinstance(result["y"], str)

    # 5. Проверка типа List[int] через typing
    x_type = mocked_annotations["x"]
    assert get_origin(x_type) is list
    assert get_args(x_type) == (int,)


# Интеграционный тест: полный цикл парсинга


def test_full_parsing_cycle(base_pazzle, form_points, form_params, setup_registry):
    """Проверяет полный цикл: маппинг имён + получение аргументов."""
    parser = PazzleParser(base_pazzle, form_points, form_params)

    # 1. Маппинг точек
    point_names = parser.map_point_names()
    assert point_names == {"a": "point_A", "b": "point_B"}

    # 2. Маппинг входных параметров
    input_param_names = parser.map_input_params_names()
    assert input_param_names == {"p1": "param_P1", "p2": "param_P2"}

    # 3. Маппинг выходных параметров
    output_param_names = parser.map_output_params_names()
    assert output_param_names == {"out1": "param_OUT1", "out2": "param_OUT2"}

    # 4. Получение аргументов конструктора
    constructor_args = parser.get_constructor_arguments()
    assert constructor_args == {
        "x": 3.14,
        "y": "hello",
        "flag": True
    }

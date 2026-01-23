import pytest
from unittest.mock import MagicMock

from CORE.run.step_interval import Interval


@pytest.fixture
def exemplar():
    """Фиктивный exemplar с методом get_point_coord."""
    ex = MagicMock()
    ex.get_point_coord.side_effect = lambda name: {
        "A": 10.0,
        "B": 20.0,
        "C": 30.0,
    }[name]
    return ex


def test_set_point_left_valid(exemplar):
    interval = Interval()
    interval.set_point_left("A")
    assert interval.left_point_name == "A"
    assert interval.left_padding is None


def test_set_point_left_conflict(exemplar):
    interval = Interval()
    interval.set_left_padding(5.0)
    with pytest.raises(ValueError, match="Невозможно установить имя левой точки: уже задан отступ для левой границы"):
        interval.set_point_left("A")


def test_set_left_padding_valid(exemplar):
    interval = Interval()
    interval.set_left_padding(5.0)
    assert interval.left_padding == 5.0
    assert interval.left_point_name is None


def test_set_left_padding_conflict(exemplar):
    interval = Interval()
    interval.set_point_left("A")
    with pytest.raises(ValueError, match="Невозможно установить отступ для левой границы: уже задано имя левой точки"):
        interval.set_left_padding(5.0)


def test_set_point_right_valid(exemplar):
    interval = Interval()
    interval.set_point_right("B")
    assert interval.right_point_name == "B"
    assert interval.right_padding is None


def test_set_point_right_conflict(exemplar):
    interval = Interval()
    interval.set_right_padding(7.0)
    with pytest.raises(ValueError, match="Невозможно установить имя правой точки: уже задан отступ для правой границы"):
        interval.set_point_right("B")


def test_set_right_padding_valid(exemplar):
    interval = Interval()
    interval.set_right_padding(7.0)
    assert interval.right_padding == 7.0
    assert interval.right_point_name is None


def test_set_right_padding_conflict(exemplar):
    interval = Interval()
    interval.set_point_right("B")
    with pytest.raises(ValueError,
                       match="Невозможно установить отступ для правой границы: уже задано имя правой точки"):
        interval.set_right_padding(7.0)


def test_validate_valid_cases(exemplar):
    # Случай 1: левая по имени, правая по отступу
    interval = Interval()
    interval.set_point_left("A")
    interval.set_right_padding(5.0)
    assert interval.validate() is True

    # Случай 2: левая по отступу, правая по имени
    interval = Interval()
    interval.set_left_padding(3.0)
    interval.set_point_right("B")
    assert interval.validate() is True


def test_validate_invalid_cases(exemplar):
    # Случай 1: обе стороны по имени — валидно, но проверим граничное
    interval = Interval()
    interval.set_point_left("A")
    interval.set_point_right("B")
    assert interval.validate() is True  # это валидно!

    # Случай 2: обе стороны по отступу — валидно
    interval = Interval()
    interval.set_left_padding(3.0)
    interval.set_right_padding(5.0)
    assert interval.validate() is True  # это тоже валидно

    # Случай 3: левая — ничего, правая — по имени
    interval = Interval()
    interval.set_point_right("B")
    assert interval.validate() is False

    # Случай 4: левая — по имени, правая — ничего
    interval = Interval()
    interval.set_point_left("A")
    assert interval.validate() is False

    # Случай 5: левая — и имя, и отступ (конфликт)
    interval = Interval()
    interval.left_point_name = "A"
    interval.left_padding = 3.0
    interval.set_point_right("B")  # правая валидна
    assert interval.validate() is False


def test_get_interval_coords_left_by_name_right_by_name(exemplar):
    interval = Interval()
    interval.set_point_left("A")
    interval.set_point_right("B")
    left, right = interval.get_interval_coords(exemplar)
    assert left == 10.0
    assert right == 20.0


def test_get_interval_coords_left_by_padding_from_right(exemplar):
    interval = Interval()
    interval.set_point_right("B")  # B = 20.0
    interval.set_left_padding(5.0)  # отступ от B влево
    left, right = interval.get_interval_coords(exemplar)
    assert left == 15.0  # 20.0 - 5.0
    assert right == 20.0


def test_get_interval_coords_right_by_padding_from_left(exemplar):
    interval = Interval()
    interval.set_point_left("A")  # A = 10.0
    interval.set_right_padding(8.0)  # отступ от A вправо
    left, right = interval.get_interval_coords(exemplar)
    assert left == 10.0
    assert right == 18.0  # 10.0 + 8.0


def test_get_interval_coords_left_by_padding_from_center(exemplar):
    interval = Interval()
    interval.set_left_padding(4.0)
    interval.set_right_padding(6.0)
    left, right = interval.get_interval_coords(exemplar, center=15.0)
    assert left == 11.0  # center - left_padding
    assert right == 21.0  # center + right_padding


def test_get_interval_coords_center_provided_but_not_used(exemplar):
    interval = Interval()
    interval.set_point_left("A")  # A = 10.0
    interval.set_point_right("B")  # B = 20.0
    with pytest.raises(ValueError, match="Параметр center был передан, но не использован при вычислениях"):
        interval.get_interval_coords(exemplar, center=100.0)

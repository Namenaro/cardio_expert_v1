from dataclasses import dataclass
from typing import Optional, Tuple

from CORE.run import Exemplar


class Interval:
    def __init__(self):
        self.left_point_name: Optional[str] = None
        self.left_padding: Optional[float] = None

        self.right_point_name: Optional[str] = None
        self.right_padding: Optional[float] = None

    def set_point_left(self, point_name: str) -> None:
        """
        Устанавливает имя левой точки.
        Если уже задан left_padding (не None), выбрасывает исключение.
        """
        if self.left_padding is not None:
            raise ValueError("Невозможно установить имя левой точки: уже задан отступ для левой границы")
        self.left_point_name = point_name

    def set_point_right(self, point_name: str) -> None:
        """
        Устанавливает имя правой точки.
        Если уже задан right_padding (не None), выбрасывает исключение.
        """
        if self.right_padding is not None:
            raise ValueError("Невозможно установить имя правой точки: уже задан отступ для правой границы")
        self.right_point_name = point_name

    def set_right_padding(self, dt: float) -> None:
        """
        Устанавливает отступ для правой границы.
        Если уже задано right_point_name (не None), выбрасывает исключение.
        """
        if self.right_point_name is not None:
            raise ValueError("Невозможно установить отступ для правой границы: уже задано имя правой точки")
        self.right_padding = dt

    def set_left_padding(self, dt: float) -> None:
        """
        Устанавливает отступ для левой границы.
        Если уже задано left_point_name (не None), выбрасывает исключение.
        """
        if self.left_point_name is not None:
            raise ValueError("Невозможно установить отступ для левой границы: уже задано имя левой точки")
        self.left_padding = dt

    def get_interval_coords(self, exemplar: Exemplar, center: Optional[float] = None) -> Tuple[float, float]:
        """
        Возвращает координаты левой и правой границ интервала.

        Логика:
        - Если для границы задано имя точки, берём её координату через exemplar.get_point_coord().
        - Если задан отступ, определяем базовую точку:
          * для левой границы: сначала пробуем правую точку (если задана по имени), иначе — center;
          * для правой границы: сначала пробуем левую точку (если задана по имени), иначе — center.
        - Если center передан, но не был использован в вычислениях, выбрасываем исключение.

        Args:
            exemplar: объект, предоставляющий метод get_point_coord() для получения координат точек
            center: опорная точка для отсчёта отступов (если другие точки не заданы)

        Returns:
            Tuple[float, float]: (левая координата, правая координата)

        Raises:
            ValueError: если невозможно определить координату или center не был использован
        """
        center_used = False  # Флаг: использовался ли center при вычислениях

        # Вычисление левой координаты
        if self.left_point_name is not None:
            # Если задано имя левой точки — берём её координату
            left_coordinate = exemplar.get_point_coord(self.left_point_name)
        elif self.left_padding is not None:
            # Если задан отступ слева — ищем базовую точку для отсчёта
            if self.right_point_name is not None:
                # Сначала пробуем правую точку (если задана по имени)
                right_point_coordinate = exemplar.get_point_coord(self.right_point_name)
                left_coordinate = right_point_coordinate - self.left_padding
            elif center is not None:
                # Иначе используем center
                left_coordinate = center - self.left_padding
                center_used = True
            else:
                raise ValueError(
                    "Невозможно определить левую координату: нет опорной точки и center не задан"
                )
        else:
            raise ValueError(
                "Левая граница не определена (не заданы ни имя точки, ни отступ)"
            )

        # Вычисление правой координаты
        if self.right_point_name is not None:
            # Если задано имя правой точки — берём её координату
            right_coordinate = exemplar.get_point_coord(self.right_point_name)
        elif self.right_padding is not None:
            # Если задан отступ справа — ищем базовую точку для отсчёта
            if self.left_point_name is not None:
                # Сначала пробуем левую точку (если задана по имени)
                left_point_coordinate = exemplar.get_point_coord(self.left_point_name)
                right_coordinate = left_point_coordinate + self.right_padding
            elif center is not None:
                # Иначе используем center
                right_coordinate = center + self.right_padding
                center_used = True
            else:
                raise ValueError(
                    "Невозможно определить правую координату: нет опорной точки и center не задан"
                )
        else:
            raise ValueError(
                "Правая граница не определена (не заданы ни имя точки, ни отступ)"
            )

        # Проверка: если center передан, но не использован — ошибка
        if center is not None and not center_used:
            raise ValueError(
                "Параметр center был передан, но не использован при вычислениях"
            )

        return left_coordinate, right_coordinate

    def validate(self) -> bool:
        """
        Проверяет корректность заполнения границ интервала.

        Валидация проходит, если для каждой границы (левой и правой) заполнено ровно одно из двух:
        - имя точки (point_name)
        - отступ (padding)

        Returns:
            bool: True, если валидация пройдена, False — иначе
        """
        # Используем преобразование в bool и XOR (^)
        left_valid = bool(self.left_point_name) ^ bool(self.left_padding)
        right_valid = bool(self.right_point_name) ^ bool(self.right_padding)
        return left_valid and right_valid

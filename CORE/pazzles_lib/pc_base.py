from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from CORE import Signal


class PCBase(ABC):
    """Базовый класс для всех классов типа "рассчитыватель параметров" """

    # Требуемая схема выходных данных - информация для парсера
    # (для автоматического внесения в базу данных)
    OUTPUT_SCHEMA: Dict[str, Tuple[type, str]] = None
    """
    Пример:
     OUTPUT_SCHEMA = {
        'error_in_procents': (float, "Ошибка интерполяции в процентах"),
        'error_in_mV': (float, "Ошибка интерполяции в мв")
    }
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Обязываем потомков заполнить OUTPUT_SCHEMA
        if cls.__name__ != "PCBase" and cls.OUTPUT_SCHEMA is None:
            raise TypeError(f"Класс {cls.__name__} должен определить OUTPUT_SCHEMA")

    @abstractmethod
    def register_points(self, *args: Any, **kwargs: Any) -> None:
        """
        Через этот метод получаем информацию о координатах точек, важных для логики пазла.
        Например, если класс реализует интерполяцию по трем точкам, то register_points
        может выглядеть так register_points(self, first_point:float, second_point:float, third_point:float)
        Обязательно написание стандартного комментария для каждой точки (через тройные кавычки).
        Другой пример: нащ параметризатор может просто измерять амплитуду сигнала в точке point.
        Тогда мы ему одну точку и регистрируем.
        """
        pass

    @abstractmethod
    def register_input_parameters(self, *args: Any, **kwargs: Any) -> None:
        """
        Регистрация других параметров формы, которые важны этому параметризацтору.
        Например,в форме
        имеется параметр "длина волны 1", "длина волны 2" и наш параметризатор, допустим,
        расчитывает процентрое соотношение этих длин, тогда этот метод может выглядеть так:
        register_input_parameters(w_len1:float, w_len2:float).
        Обязательно написание стандартного комментария для каждого параметра (через тройные кавычки).

        """
        pass

    @abstractmethod
    def run(self, signal: Signal) -> Dict[str, Any]:
        """
        Выполнение алгоритма. Предполагается, что перед запуском этого метода методы регистрации
        входных точек и входных параметров уже запускались.

        :param signal: Входной сигнал для анализа
        :return: Результаты расчета параметров {имя_параметра :его_вычисленное_значение}
        """
        pass

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from CORE import Signal


class HCBase(ABC):
    """Базовый класс для всех классов типа "жесткое условие на параметры" """

    @abstractmethod
    def register_input_parameters(self, *args: Any, **kwargs: Any) -> None:
        """
        Регистрация параметров формы, на которые накладывается данное жесткое условие.
        Например,в форме
        имеется параметр "длина волны 1", "длина волны 2" и наше жесткое условие требует, чтобы их сумма была не менее чем 3, тогда этот метод может выглядеть так:
        register_input_parameters(w_len1:float, w_len2:float).
        Обязательно написание стандартного комментария для каждого параметра (через тройные кавычки).

        """
        pass

    @abstractmethod
    def run(self) -> bool:
        """
        Проверка жесткого условия. Предполагается, что перед запуском этого метода метод регистрации
        входных параметров уже запускался.

        :return: выполнено условие или нет
        """
        pass

from typing import Any, Dict, Tuple, Optional, List

from CORE import Signal
from CORE.db_dataclasses import Form
from CORE.logger import get_logger

logger = get_logger(__name__)
from CORE.exeptions import CoreError


class Exemplar:
    """ Экземпляр формы — конкретная расстановка точек на конкретном одномерном сигнале ЭКГ.
    С каждым шагом установки этот экземпляр получает новые точки и параметры, и таким образом "растет".
    Класс представляет собой геттеры-сеттеры с над точками, параметрами и оценкой экземпляра.
    По ходу роста оценка меняется из-вне. Перезапись существующих точек и параметров вызовет исключения.
    """

    def __init__(self, signal: Signal):
        """
        :param signal: объект сигнала, на котором размещаются точки
        """
        self.signal = signal
        self._points: Dict[str, Tuple[float, int]] = {}  # Хранилище точек: имя -> (координата, track_id)
        self._parameters: Dict[str, Any] = {}  # Хранилище параметров: имя -> значение
        self.evaluation_result: Optional[float] = None

        self.failed_HCs_ids: [List[int]] = []  # id проваленных жестких условий.
        self.passed_HCs_ids: [List[int]] = []  # id успешно выполнившихся жестких условий.

    def get_param_names(self) -> List[str]:
        return list(self._parameters.keys())

    def add_point(self, point_name: str, point_coord_t: float, track_id: Any) -> bool:
        """
        Добавляет точку на сигнал.

        :param point_name: имя точки
        :param point_coord_t: временная координата точки в секундах
        :param track_id: идентификатор трека, связанный с точкой
        :return: True, если точка добавлена, False, если координата вне диапазона сигнала

        :raises ValueError: при попытке перезаписи
        """
        # Проверяем, что имя точки ещё не используется
        if point_name in self._points:
            raise CoreError(f"Точка {point_name} уже сущетсвует, не должно возникать попыток перезаписи")

        # Проверяем, что момент времени находится в пределах сигнала
        if not self.signal.is_moment_in_signal(point_coord_t):
            return False

        # Добавляем точку (сохраняем пару: координата + track_id)
        self._points[point_name] = (point_coord_t, track_id)
        return True

    def contains_point(self, point_name: str) -> bool:
        """
        Проверяет наличие точки с заданным именем.

        :param point_name: имя точки
        :return: True, если точка существует, False иначе
        """
        return point_name in self._points

    def get_point_coord(self, point_name: str) -> Optional[float]:
        """
        Возвращает временную координату точки.

        :param point_name: имя точки
        :return: временная координата точки в секундах, None если точка не найдена
        """
        if not self.contains_point(point_name):
            return None

        return self._points[point_name][0]  # Возвращаем только координату (первый элемент пары)

    def get_point_track_id(self, point_name: str) -> Any:
        """
        Возвращает track_id точки.

        :param point_name: имя точки
        :return: идентификатор трека, связанный с точкой
        :raises ValueError: если точка не найдена
        """
        if not self.contains_point(point_name):
            raise CoreError(f"Точка {point_name} не найдена")

        return self._points[point_name][1]  # Возвращаем track_id (второй элемент пары)

    def add_parameter(self, param_name: str, param_value: Any) -> None:
        """
        Добавляет параметр в экземпляр формы.

        :param param_name: имя параметра (должно быть уникальным)
        :param param_value: значение параметра
        :raises ValueError если попытка перезаписи параметра
        """

        # Если параметр уже существует
        if param_name in self._parameters:
            raise CoreError(f"{param_name} уже сущетсвует, не должно возникать попыток перезаписи")

        self._parameters[param_name] = param_value


    def contains_parameter(self, param_name: str) -> bool:
        """
        Проверяет наличие параметра с заданным именем.

        :param param_name: имя параметра
        :return: True, если параметр существует, False иначе
        """
        return param_name in self._parameters

    def get_parameter_value(self, param_name: str) -> Optional[Any]:
        """
        Возвращает значение параметра.

        :param param_name: имя параметра
        :return: значение параметра, None если параметр не найден
        """
        if not self.contains_parameter(param_name):
            return None

        return self._parameters[param_name]

    def get_signal(self) -> Signal:
        """
        Возвращает связанный сигнал.

        :return: объект сигнала
        """
        return self.signal

    @property
    def evaluation_result(self) -> Optional[float]:
        """
        Возвращает результат оценки.

        :return:  результат оценки этого экземпляра или None, если оценка еще не производилась
        """
        return self._evaluation_result

    @evaluation_result.setter
    def evaluation_result(self, value: Optional[float]) -> None:
        """
        Устанавливает результат оценки.

        :param value: оценка "хорошести" этого экземпляра
        :raises TypeError: если значение не является float
        :raises ValueError: если значение выходит за допустимый диапазон
        """
        # Валидация типа
        if value is not None and not isinstance(value, float):
            raise CoreError("evaluation_result должно быть float или None")

        # Валидации диапазона
        if isinstance(value, float) and not (0 <= value <= 1):
            raise CoreError("evaluation_result должно быть в диапазоне")

        self._evaluation_result = value

    def __len__(self):
        return len(self._points)


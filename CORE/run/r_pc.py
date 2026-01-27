from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from CORE.db_dataclasses import BasePazzle, Point, Parameter
from CORE.pazzles_lib.pc_base import PCBase
from CORE.run import Exemplar
from CORE.run.run_pazzle import PazzleParser


class R_PC:
    @dataclass
    class Result:
        """
        Класс для хранения результата выполнения пазла.

        Поля:
        - status: флаг успешности выполнения (True/False)
        - params_measurement: словарь с результатами измерений
        - absent_input_params: список отсутствующих входных параметров
        - absent_input_points: список отсутствующих точек
        - err_msg: текстовое описание ошибки (если возникла)
        """
        status: bool = True
        params_measurement: Dict[str, Any] = field(default_factory=dict)
        absent_input_params: List[str] = field(default_factory=list)
        absent_input_points: List[str] = field(default_factory=list)
        err_msg: Optional[str] = None

    def __init__(self, base_pazzle: BasePazzle, form_points: List[Point], form_params: List[Parameter]):
        """
        Инициализация экземпляра R_PC.

        Args:
            base_pazzle: базовый пазл (описание класса пазла)
            form_points: список точек формы
            form_params: список параметров формы
        """
        self.base_pazzle = base_pazzle
        self.form_points = form_points
        self.form_params = form_params

    def run(self, exemplar: Exemplar) -> R_PC.Result:
        """
        Основной метод выполнения пазла на конкретном экземпляре.

        Выполняет последовательность шагов:
        1. Создание runnable-объекта (экземпляра класса пазла)
        2. Сбор данных точек из экземпляра
        3. Сбор данных параметров из экземпляра
        4. Настройка runnable-объекта
        5. Запуск и получение результата

        Args:
            exemplar: экземпляр формы для обработки

        Returns:
            Объект Result с результатами выполнения
        """
        result = self.Result()
        parser = PazzleParser(self.base_pazzle, form_points=self.form_points, form_params=self.form_params)

        # 1. Создание runnable-объекта
        runnable = self._create_runnable(parser, result)
        if not runnable:
            return result

        # 2. Сбор данных точек
        input_points_data = self._collectinput_points(parser, exemplar, result)
        if not result.status:
            return result

        # 3. Сбор данных параметров
        input_params_data = self._collect_input_params(parser, exemplar, result)
        if not result.status:
            return result

        # 4. Настройка runnable
        runnable.register_points(**input_points_data)
        runnable.register_input_parameters(**input_params_data)

        # 5. Запуск и получение результата
        return self._execute_runnable(runnable, exemplar.signal, result)

    def _create_runnable(self, parser: PazzleParser, result: R_PC.Result) -> Optional[PCBase]:
        """
        Создает экземпляр класса пазла (runnable-объект).

        Args:
            parser: объект парсера для получения информации о классе пазла
            result: объект результата для записи ошибок

        Returns:
            Экземпляр класса пазла или None в случае ошибки

        """
        try:
            cls = parser.get_cls()
            args = parser.get_constructor_arguments()
            return cls(**args)
        except Exception as e:
            result.status = False
            result.err_msg = str(e)
            return None

    def _collectinput_points(self, parser: PazzleParser, exemplar: Exemplar, result: R_PC.Result) -> Dict[str, float]:
        """
        Собирает данные точек из экземпляра формы.

        Args:
            parser: объект парсера для получения соответствия имен точек
            exemplar: экземпляр формы
            result: объект результата для записи ошибок и отсутствующих точек

        Returns:
            Словарь соответствия имен точек класса и их координат в экземпляре
        """
        try:
            required_points = parser.map_point_names()
        except Exception as e:
            result.status = False
            result.err_msg = f"Не удалось получить список имён необходимых PC-пазлу {self.base_pazzle.id} входных точек: {e}"
            return {}

        input_points_data = {}
        for class_point_name, exemplar_point_name in required_points.items():
            point_coord = exemplar.get_point_coord(exemplar_point_name)
            if point_coord is None:
                result.absent_input_points.append(exemplar_point_name)
                result.status = False
            else:
                input_points_data[class_point_name] = point_coord

        return input_points_data

    def _collect_input_params(self, parser: PazzleParser, exemplar: Exemplar, result: R_PC.Result) -> Dict[str, Any]:
        """
        Собирает значения параметров из экземпляра формы.

        Args:
            parser: объект парсера для получения соответствия имен параметров
            exemplar: экземпляр формы
            result: объект результата для записи ошибок и отсутствующих параметров

        Returns:
            Словарь соответствия имен параметров класса и их значений в экземпляре
        """
        try:
            required_params = parser.map_input_params_names()
        except Exception as e:
            result.status = False
            result.err_msg = f"Не удалось получить список имён необходимых PC-пазлу {self.base_pazzle.id} входных параметров: {e}"
            return {}

        input_params_data = {}
        for class_param_name, exemplar_param_name in required_params.items():
            param_value = exemplar.get_parameter_value(exemplar_param_name)
            if param_value is None:
                result.absent_input_params.append(exemplar_param_name)
                result.status = False
            else:
                input_params_data[class_param_name] = param_value

        return input_params_data

    def _execute_runnable(self, runnable: PCBase, signal: Any, result: R_PC.Result) -> R_PC.Result:
        """
        Запускает выполнение runnable-объекта на сигнале.

        Args:
            runnable: экземпляр класса пазла для выполнения
            signal: сигнал для обработки
            result: объект результата для записи ошибки при необходимости

        Returns:
            Объект Result с обновленными данными (результатами или ошибкой)
        """
        try:
            result.params_measurement = runnable.run(signal)
        except Exception as e:
            result.status = False
            class_name = self.base_pazzle.class_ref.name
            result.err_msg = f"Возникла внутренняя ошибка в классе {class_name}: {str(e)}"
        return result

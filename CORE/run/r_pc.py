from __future__ import annotations

import logging
from typing import Dict, Any, List, Tuple

from CORE.db_dataclasses import BasePazzle, Point, Parameter
from CORE.exeptions import RunPazzleError, PazzleOutOfSignal
from CORE.pazzles_lib.pc_base import PCBase
from CORE.run import Exemplar
from CORE.run.run_pazzle import PazzleParser


class R_PC:
    """ Класс измерителя параметров. Принимает экземпляр с частично заполннными
    точками/параметроми и проводит замер некоторых новых параметров,
    которым он посвещен"""
    def __init__(self, base_pazzle: BasePazzle, form_points: List[Point], form_params: List[Parameter]):
        """
        Инициализация экземпляра R_PC из класса, служащего (де)сериализаци из БД.

        :param base_pazzle: базовый пазл (описание класса пазла)
        :param form_points: список точек формы
        :param form_params: список параметров формы
        """
        self.base_pazzle = base_pazzle
        self.form_points = form_points
        self.form_params = form_params

    def run(self, exemplar: Exemplar) -> Dict[str, Any]:
        """
        Основной метод выполнения пазла на конкретном экземпляре.

        Выполняет последовательность шагов:
        1. Создание runnable-объекта (экземпляра класса пазла)
        2. Сбор данных точек из экземпляра
        3. Сбор данных параметров из экземпляра
        4. Настройка runnable-объекта
        5. Запуск и получение результата
        6. Ремампинг имен параметров из сигнатуры класса в соотвествющие имена параметров из сигнутры формы

        :param exemplar: экземпляр формы для обработки
        :raise PazzleOutOfSignal: если логика пазла потребовала обращения за пределы предоставленного сигнала
        :raise RunPazzleError: различные ошибки выполнения пазла
        :return Словарь с результатами измерений {имя_параметра_в форме: его померенное значение}
        """
        parser = PazzleParser(self.base_pazzle, form_points=self.form_points, form_params=self.form_params)

        # 1. Создание runnable-объекта
        runnable = self._create_runnable(parser)

        # 2. Сбор данных точек
        points_data, absent_points = self._collect_input_points(parser, exemplar)
        if absent_points:
            raise RunPazzleError.missing_input_points(self.base_pazzle.id, absent_points)

        # 3. Сбор данных параметров
        params_data, absent_params = self._collect_input_params(parser, exemplar)
        if absent_params:
            raise RunPazzleError.missing_input_params(self.base_pazzle.id, absent_params)

        # 4. Настройка runnable
        runnable.register_points(**points_data)
        runnable.register_input_parameters(**params_data)

        # 5. Запуск и получение результата
        measurement_res = self._execute_runnable(runnable, exemplar.signal)

        # 6. Ремампинг имен параметров из сигнатуры класса в соотвествющие имена из сигнутры формы
        return self._remap_output_params_to_form_params(measurement_res, parser)

    def _create_runnable(self, parser: PazzleParser) -> PCBase:
        """
        Создает экземпляр класса пазла (runnable-объект).

        :param parser: объект парсера для получения информации о классе пазла
        :raise RunPazzleError: если не удалось создать экземпляр класса
        :return Экземпляр класса пазла
        """
        try:
            cls = parser.get_cls()
            args = parser.get_constructor_arguments()
            return cls(**args)
        except Exception as e:
            raise RunPazzleError.class_creation_failed(self.base_pazzle.id, str(e))

    def _collect_input_points(self, parser: PazzleParser, exemplar: Exemplar) -> Tuple[Dict[str, float], List[str]]:
        """
        Собирает данные точек из экземпляра формы.

        :param parser: объект парсера для получения соответствия имен точек
        :param exemplar: экземпляр формы
        :raise RunPazzleError: если не удалось получить соответствие имен точек
        :return Кортеж (словарь с данными точек, список отсутствующих точек)
        """
        # Получение соответствия имен точек
        try:
            required_points = parser.map_point_names()
        except Exception as e:
            raise RunPazzleError.points_mapping_failed(self.base_pazzle.id, str(e))

        # Сбор данных точек
        points_data = {}
        absent_points = []

        for class_point_name, exemplar_point_name in required_points.items():
            point_coord = exemplar.get_point_coord(exemplar_point_name)
            if point_coord is None:
                absent_points.append(exemplar_point_name)
            else:
                points_data[class_point_name] = point_coord

        return points_data, absent_points

    def _collect_input_params(self, parser: PazzleParser, exemplar: Exemplar) -> Tuple[Dict[str, Any], List[str]]:
        """
        Собирает значения параметров из экземпляра формы.

        :param parser: объект парсера для получения соответствия имен параметров
        :param exemplar: экземпляр формы
        :raise RunPazzleError: если не удалось получить соответствие имен параметров
        :return Кортеж (словарь с данными параметров, список отсутствующих параметров)
        """
        # Получение соответствия имен параметров
        try:
            required_params = parser.map_input_params_names()
        except Exception as e:
            raise RunPazzleError.params_mapping_failed(self.base_pazzle.id, str(e))

        # Сбор данных параметров
        params_data = {}
        absent_params = []

        for class_param_name, exemplar_param_name in required_params.items():
            param_value = exemplar.get_parameter_value(exemplar_param_name)
            if param_value is None:
                absent_params.append(exemplar_param_name)
            else:
                params_data[class_param_name] = param_value

        return params_data, absent_params

    def _execute_runnable(self, runnable: PCBase, signal: Any) -> Dict[str, Any]:
        """
        Запускает выполнение runnable-объекта на сигнале.

        :param runnable: экземпляр класса пазла для выполнения
        :param signal: сигнал для обработки
        :raise PazzleOutOfSignal: если пазл запросил данные за пределами сигнала
        :raise RunPazzleError: другие ошибки выполнения пазла
        :return Словарь с результатами измерений
        """
        try:
            return runnable.run(signal)
        except PazzleOutOfSignal as e:
            # Дописываем имя класса и пробрасываем дальше
            if not e.class_name:
                e.class_name = self.base_pazzle.class_ref.name
            raise
        except Exception as e:
            class_name = self.base_pazzle.class_ref.name
            raise RunPazzleError.execution_error(self.base_pazzle.id, class_name, str(e))

    def _remap_output_params_to_form_params(
            self,
            params_of_class_calculated: Dict[str, Any],
            parser: PazzleParser
    ) -> Dict[str, Any]:
        """
        Преобразует словарь параметров: заменяет ключи (имена из сигнатуры класса)
        на соответствующие имена параметров формы.

        :param params_of_class_calculated: {имя параметра в сигнатуре: значение}
        :param parser: объект, предоставляющий отображение имён
        :return: {имя параметра в форме: значение}
        """
        cls_names_to_form_names: Dict[str, str] = parser.map_output_params_names()

        return {
            form_name: params_of_class_calculated[cls_name]
            for cls_name, form_name in cls_names_to_form_names.items()
            if cls_name in params_of_class_calculated
        }

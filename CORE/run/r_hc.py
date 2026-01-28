from __future__ import annotations

from typing import Dict, Any, List, Tuple

from CORE.db_dataclasses import BasePazzle, Parameter
from CORE.exeptions import RunPazzleError
from CORE.pazzles_lib.hc_base import HCBase
from CORE.run import Exemplar
from CORE.run.run_pazzle import PazzleParser


class R_HC:
    def __init__(self, base_pazzle: BasePazzle, form_params: List[Parameter]):
        """
        Инициализация экземпляра R_HC из класса, служащего (де)сериализаци из БД.

        :param base_pazzle: базовый пазл (описание класса пазла)
        :param form_params: список параметров формы
        """
        self.base_pazzle = base_pazzle
        self.form_params = form_params

    def run(self, exemplar: Exemplar) -> bool:
        """
        Основной метод выполнения пазла на конкретном экземпляре.

        Выполняет последовательность шагов:
        1. Создание runnable-объекта (экземпляра класса пазла)
        2. Сбор данных параметров из экземпляра
        3. Настройка runnable-объекта
        4. Запуск и получение результата

        :param exemplar: экземпляр формы для обработки
        :raise RunPazzleError: различные ошибки выполнения пазла
        :return Флаг выполнения условия (is_condition_fitted)
        """
        parser = PazzleParser(self.base_pazzle, form_points=[], form_params=self.form_params)

        # 1. Создание runnable-объекта
        runnable = self._create_runnable(parser)

        # 2. Сбор данных параметров
        params_data, absent_params = self._collect_input_params(parser, exemplar)
        if absent_params:
            raise RunPazzleError.missing_input_params(self.base_pazzle.id, absent_params)

        # 3. Настройка runnable
        runnable.register_input_parameters(**params_data)

        # 4. Запуск и получение результата
        return self._execute_runnable(runnable)

    def _create_runnable(self, parser: PazzleParser) -> HCBase:
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

    def _execute_runnable(self, runnable: HCBase) -> bool:
        """
        Запускает выполнение runnable-объекта.

        :param runnable: экземпляр класса пазла для выполнения
        :raise PazzleOutOfSignal: если пазл запросил данные за пределами сигнала
        :raise RunPazzleError: другие ошибки выполнения пазла
        :return Флаг выполнения условия (is_condition_fitted)
        """
        try:
            return runnable.run()

        except Exception as e:

            class_name = self.base_pazzle.class_ref.name
            raise RunPazzleError.execution_error(self.base_pazzle.id, class_name, str(e))

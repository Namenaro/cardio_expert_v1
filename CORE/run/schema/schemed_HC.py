from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict, Tuple

from CORE.run.run_pazzle import PazzleParser
from CORE.run.schema.context import Context


class HC_Wrapper:
    def __init__(self, pazzle, form_params: List[Parameter]):
        parser = PazzleParser(base_pazzle=pazzle, form_params=form_params, form_points=[])
        map_class_to_form_params: Dict[str, str] = parser.map_input_params_names()

        self.required_params_names: List[str] = list(map_class_to_form_params.values())
        self.hc = pazzle

    def requred_params_names(self) -> List[str]:
        """
        Имена параметров формы, которые должны быть уже посчитаны перед запуском этого пазла
        :return: список имён требуемых параметров
        """
        return self.required_params_names

    def get_pazzle_obj(self) -> BasePazzle:
        """ Получить незапускаемый объект пазла, над которым сделана эта обертка"""
        return self.hc

    def detect_missing_input_params(self, params_names_in_context: List[str]) -> List[str]:
        """
        Проверяет, какие из требуемых параметров отсутствуют в текущем контексте.

        :param params_names_in_context: имена параметров формы, которые уже посчитаны по схеме к этому шагу
        :return:
            - пустой список [], если все требуемые параметры присутствуют (можно запускать пазл);
            - список недостающих имён параметров, если какие‑то отсутствуют.
        """

        required_set = set(self.required_params_names)
        context_set = set(params_names_in_context)

        assert len(context_set) == len(params_names_in_context)
        missing_params = required_set - context_set
        return sorted(list(missing_params))

    def fit_context(self, context: Context) -> Tuple[bool, List[str]]:
        """
        Проверяет, достаточно ли данных в текущем контексте для запуска этого пазла.

        :param context: объект контекста, содержащий уже вычисленные параметры и другие данные
        :return: кортеж из:
            - bool: True, если все требуемые параметры присутствуют (можно запускать пазл);
            - List[str]: список недостающих параметров (пустой, если всё есть).
        """

        params_in_context = context.params_done
        missing_params = self.detect_missing_input_params(params_in_context)
        is_ready = len(missing_params) == 0

        return is_ready, missing_params

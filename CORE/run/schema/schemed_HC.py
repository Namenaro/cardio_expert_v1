from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict, Tuple

from CORE.run.run_pazzle import PazzleParser
from CORE.run.schema.context import Context


class HC_Wrapper:
    """ Вспомогательный клас, нужный для расчета схемы"""
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

    def fit_context(self, context: Context) -> Tuple[bool, List[str]]:
        """
        Проверяет, достаточно ли данных в текущем контексте для запуска этого пазла.


        :param context: объект контекста, содержащий уже вычисленные параметры и другие данные
        :return: кортеж из:
            - bool: True, если все требуемые параметры присутствуют (можно запускать пазл);
            - List[str]: список недостающих параметров (пустой, если всё есть).
        """
        # Получаем имена уже посчитанных параметров из контекста
        available_params = set(context.params_done)

        # Преобразуем требуемые параметры в множество для эффективной проверки
        required_params = set(self.required_params_names)

        # Находим недостающие параметры (разность множеств)
        missing_params = sorted(list(required_params - available_params))

        # Проверяем, есть ли недостающие параметры
        is_ready = len(missing_params) == 0

        return is_ready, missing_params

    def __str__(self):
        text = f"[ id: {self.hc.id} для {', '.join(self.required_params_names)}]"

        return text

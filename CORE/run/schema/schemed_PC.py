from typing import List, Dict, Tuple

from CORE.db_dataclasses import Point, BasePazzle, Parameter
from CORE.run.run_pazzle import PazzleParser
from CORE.run.schema.context import Context


class PC_Wrapper:
    """ Вспомогательный клас, нужный для расчета схемы"""
    def __init__(self, pazzle: BasePazzle, form_params: List[Parameter], form_points: List[Point]):
        self.pc = pazzle
        parser = PazzleParser(base_pazzle=pazzle, form_params=form_params, form_points=form_points)

        # входные параметры, которые требует этот пазл (их имена в форме)
        cls_names_to_form_names_input: Dict[str, str] = parser.map_input_params_names()
        self.required_params_names: List[str] = list(cls_names_to_form_names_input.values())

        # выходные параметры, которые выдает этот пазл (их имена в форме)
        cls_names_to_form_names_output: Dict[str, str] = parser.map_output_params_names()
        self.returned_params_names: List[str] = list(cls_names_to_form_names_output.values())

        # входные точки, которые требует этот пазл (их имена в форме)
        cls_points_to_form_points: Dict[str, str] = parser.map_point_names()
        self.required_points_names: List[str] = list(cls_points_to_form_points.values())

    def requred_params(self) -> List[str]:
        return self.required_params_names

    def returned_params(self) -> List[str]:
        return self.returned_params_names

    def requred_points(self) -> List[str]:
        return self.required_points_names

    def fit_context(self, context: Context) -> Tuple[bool, List[str], List[str]]:
        """
        Проверяет, достаточно ли данных в текущем контексте для запуска этого пазла.

        :param context: объект контекста, содержащий уже вычисленные параметры и другие данные
        :return: кортеж из:
            - bool: True, если все требуемые параметры и точки присутствуют (можно запускать пазл);
            - List[str]: список недостающих параметров (пустой, если всё есть);
            - List[str]: список недостающих точек (пустой, если всё есть).
        """
        # Получаем списки уже имеющихся данных из контекста
        available_params = set(context.params_done)
        available_points = set(context.points_done)

        # Преобразуем требуемые данные в множества для эффективного сравнения
        required_params_set = set(self.required_params_names)
        required_points_set = set(self.required_points_names)

        # Находим недостающие элементы
        missing_params = sorted(list(required_params_set - available_params))
        missing_points = sorted(list(required_points_set - available_points))

        # Проверяем, есть ли хоть что‑то недостающее
        is_ready = len(missing_params) == 0 and len(missing_points) == 0

        return is_ready, missing_params, missing_points

    def __str__(self):
        text = f"[ id: {self.pc.id} возвращает {', '.join(self.returned_params())}, требует "
        if self.required_params_names:
            text += f"параметры {', '.join(self.required_params_names)}    "
        if self.required_points_names:
            text += f"точки {', '.join(self.required_points_names)}"
        text += "] "
        return text

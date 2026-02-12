from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict, Tuple

from CORE.exeptions import SchemaError
from CORE.run.run_pazzle import PazzleParser
from CORE.run.schema.context import Context
from CORE.run.schema.schemed_HC import HC_Wrapper
from CORE.run.schema.schemed_PC import PC_Wrapper
from DA3.form_widgets.hcs_widget.HC_card import HCCard


class SchemedStep:
    """ Вспомогательный клас, нужный для расчета схемы"""

    def __init__(self, step: Step):
        self.step: Step = step

        self.wPCs: List[PC_Wrapper] = []
        self.wHCs: List[HC_Wrapper] = []

        # Если шагу необходимы уже ранее поставленные точки:
        self.required_points_names: List[str] = []

        if step.left_point:
            self.required_points_names.append(step.left_point.name)
        if step.right_point:
            self.required_points_names.append(step.right_point.name)

    def to_text(self) -> str:
        text = f"\n ШАГ {self.step.num_in_form}--------------------------------------\n Целевая: {self.step.target_point.name}"
        text += f"\n Опорные: {'  '.join(self.required_points_names)}"
        text += f"\n PCs: {'  '.join([str(wpc.pc.id) for wpc in self.wPCs])}"
        text += f"\n HCs: {'  '.join([str(whc.hc.id) for whc in self.wHCs])}\n"

        return text

    def required_points_names(self) -> List[str]:
        return self.required_points_names

    def get_step_obj(self) -> Step:
        return self.step

    def fit_interval(self, context: Context) -> Tuple[bool, List[str]]:
        """
        Проверяет, есть ли в контексте точки для интервала
        :param context: объект контекста, содержащий уже имена вычисленных сущностей (точки, параметры, ...)
        :return: кортеж из:
            - bool: True, если все требуемые точки присутствуют;
            - List[str]: список недостающих точек (пустой, если всё есть).
        """
        absent_names = []
        points_names_in_context = set(context.points_done)
        for name in self.required_points_names:
            if name not in points_names_in_context:
                absent_names.append(name)

        if len(absent_names):
            return False, absent_names

        return True, absent_names

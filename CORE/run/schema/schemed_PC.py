from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict

from CORE.run.run_pazzle import PazzleParser


class PC_Wrapper:
    def __init__(self, pazzle: BasePazzle, form_params: List[Parameter], form_points: List[Point]):
        self.pc = pazzle

        parser = PazzleParser(base_pazzle=pazzle, form_params=form_params, form_points=form_points)

    def requred_params(self):
        pass

    def returned_params(self):
        pass

    def requred_points(self):
        pass

from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict

from CORE.run.run_pazzle import PazzleParser


class ShemaErrors(Enum):
    NO_PCS = "NO_PCS -> должен быть хоть один измеритель параметра"
    NO_POINTS = "NO_POINTS -> должна быть хоть одна точка"


class FormWrapper:
    def __init__(self, form: Form):
        self.points = form.points
        self.parameters = form.parameters

        self.steps = form.steps
        self.wHCs = [obj for obj in form.HC_PC_objects if obj.is_HC()]
        self.wPCs = [obj for obj in form.HC_PC_objects if obj.is_PC()]


class Schema:
    def __init__(self, form: Form):
        self.errors: List[ShemaErrors] = []

    def is_failed(self):
        return len(self.errors) > 0

    def get_PCs_by_step_num(self, step_num) -> List[BasePazzle]:
        pass

    def get_HCs_by_step_num(self, step_num) -> List[BasePazzle]:
        pass

    def __str__(self):
        pass

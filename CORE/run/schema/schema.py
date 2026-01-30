from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict, Tuple

from CORE.run.run_pazzle import PazzleParser
from CORE.run.schema.context import Context
from CORE.run.schema.schemed_HC import HC_Wrapper
from CORE.run.schema.schemed_PC import PC_Wrapper
from DA3.form_widgets.hcs_widget.HC_card import HCCard


class Code(ENUM):
    pass





class Schema:
    def __init__(self, form: Form):
        self.form = form
        self.context = Context()

        self.steps_sorted: List[Step] = []

    def _init_HC_PC(self):
        try:
            self.wHCs = [HC_Wrapper(obj, form_params=self.form.parameters)
                         for obj in self.form.HC_PC_objects
                         if obj.is_HC()
                         ]
            self.wPCs = [PC_Wrapper(obj, form_params=self.form.parameters, form_points=self.form.points)
                         for obj in self.form.HC_PC_objects
                         if obj.is_PC()]
        except Exception as e:
            self.context.

    def get_PCs_by_step_num(self, step_num) -> List[BasePazzle]:
        pass

    def get_HCs_by_step_num(self, step_num) -> List[BasePazzle]:
        pass

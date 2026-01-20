from typing import Any

from CORE.db_dataclasses import BasePazzle, BaseClass


class RunPazzle:
    def __init__(self):
        pass

    def _init_obj(self, pazzle: BasePazzle) -> BaseClass:
        class_name = pazzle.class_ref.name
        constructor_args_dict = pazzle.argument_values

    def run(self, pazzle: BasePazzle, signal, left, right) -> Any:
        match pazzle:
            case pazzle.is_HC():
                return self.run_HC(pazzle, signal, left=left, right=right)
            case pazzle.is_PC():
                return self.run_PC(pazzle, signal, left=left, right=right)

    def run_HC(self, hc_pazzle: BasePazzle, signal, left, right):
        pass

    def run_PC(self, pc_pazzle: BasePazzle, signal, left, right):
        pass

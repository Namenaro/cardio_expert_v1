from typing import Any, Dict

from CORE.db_dataclasses import BasePazzle, BaseClass
from CORE.pazzles_lib.pc_base import PCBase
from CORE.run.run_pazzle import factory

class RunPazzle:
    def __init__(self):
        pass

    def _init_obj(self, pazzle: BasePazzle) -> BaseClass:
        class_name = pazzle.class_ref.name
        constructor_args_dict = pazzle.argument_values

    def _create_runnable(self, pazzle: BasePazzle) -> Any:
        classname = pazzle.class_ref.name
        constructor_args: Dict[str, str] = pazzle.get_args_names_to_vals()
        runnable = factory.create(classname=classname, args=constructor_args)
        return runnable

    def run_HC(self, hc_pazzle: BasePazzle, signal):
        runnable = self._create_runnable(pazzle=hc_pazzle)

    def run_PC(self, pc_pazzle: BasePazzle, signal):
        runnable: PCBase = self._create_runnable(pazzle=pc_pazzle)
        runnable.register_points()
        runnable.register_input_parameters()
        args_dict = runnable.run(signal)

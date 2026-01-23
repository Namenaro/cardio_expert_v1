from typing import Any, Dict, Optional

from CORE import Signal
from CORE.db_dataclasses import BasePazzle, BaseClass
from CORE.pazzles_lib.pc_base import PCBase
from CORE.run import Exemplar
from CORE.run.run_pazzle import factory

class RunPazzle:
    def __init__(self):
        pass

    def _create_runnable(self, pazzle: BasePazzle) -> Any:
        classname = pazzle.class_ref.name
        constructor_args: Dict[str, str] = pazzle.get_args_names_to_vals()
        runnable = factory.create(classname=classname, args=constructor_args)
        return runnable

    def run_HC(self, hc_pazzle: BasePazzle, signal):
        runnable = self._create_runnable(pazzle=hc_pazzle)

    def run_PC(self, pc_pazzle: BasePazzle, signal: Signal, exemplar: Exemplar) \
            -> Optional[Dict[str, Any]]:
        """

        :param pc_pazzle:
        :param signal:
        :param exemplar:
        :return: если None, то для расчета этих параметров чего-то еще не х   
        """
        runnable: PCBase = self._create_runnable(pazzle=pc_pazzle)
        runnable.register_points()
        runnable.register_input_parameters()
        params_names_to_vals: Dict[str, Any] = runnable.run(signal)
        return params_names_to_vals

    def _get_input_points_coords(self, exemplar, pazzle) -> Optional[Dict[str, float]]:
        """

        :param exemplar:
        :param pazzle:
        :return: если None, то нужных точек в экземпляре еще нет (хотя бы одной)
        """
        pass

    def _get_input_params_values(self, exemplar, pazzle) -> Optional[Dict[str, Any]]:
        """

        :param exemplar:
        :param pazzle:
        :return: если None, то нужных параметров в экземпляре еще нет (хотя бы одного)
        """

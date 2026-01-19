from CORE import Signal
from CORE.db_dataclasses import Form
from CORE.run import Exemplar
from CORE.run.run_pazzle import RunPazzle


class Parametriser:
    def __init__(self, form: Form, run_pazzle: RunPazzle):
        self.run_pazzle = run_pazzle

        self.PCs = [obj for obj in form.HC_PC_objects if obj.is_PC()]
        self.HCs = [obj for obj in form.HC_PC_objects if obj.is_HC()]

    def parametrise_exemplar(self, exemplar: Exemplar) -> bool:
        # перебираем все  PC и заполяем все параметры которые можем
        for PC in self.PCs:
            self.run_pazzle.run_PC(PC, signal=exemplar.signal, left=, right=)

        # перебираем все HC и если хоть одно наружено, возвращаем False, иначе True
        return True

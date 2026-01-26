from CORE.db_dataclasses import BasePazzle
from CORE.run import Exemplar


class R_PC:
    def __init__(self, base_pazzle: BasePazzle):
        self.base_pazzle = base_pazzle

        cls = get_cls(base_pazzle)
        args = get_construcor_arguments(base_pazzle)
        self.runnable = create_runnable(cls, args)

    def run(self, exemplar: Exemplar):

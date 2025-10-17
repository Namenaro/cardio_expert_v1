from CORE.dataclasses.step import Step
from CORE.dataclasses.point import Point
from CORE.dataclasses.parameter import Parameter
from CORE.dataclasses.SM_PC_HC_PS import PC_ObjectEntry, HC_ObjectEntry

from typing import List, Set
from dataclasses import dataclass, field

@dataclass
class Form:
        name: str
        comment: str = ""

        # точки формы
        points: Set[Point] = field(default_factory=set)

        # параметры формы
        parameters: Set[Parameter] = field(default_factory=set)

        # шаги установки точек формы, их столько сколько точек в форме, порядок в этом списке очень важен
        steps: List[Step] = field(default_factory=list)

        # измерители параметров
        PCs: List[PC_ObjectEntry] = field(default_factory=list)

        # проверяльщики жестких условий на параметры
        HCs: List[HC_ObjectEntry] = field(default_factory=list)

        def is_valid(self) -> bool:
            conditions = (
                all(step.is_valid() for step in self.steps),
                len(self.steps) == len(self.points),
                len(self.parameters) > 0,
                len(self.points) > 0
            )
            return all(conditions)


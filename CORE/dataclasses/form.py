from CORE.dataclasses.step import Step
from CORE.dataclasses.point import Point
from CORE.dataclasses.parameter import Parameter
from CORE.dataclasses.SM_PC_HC_PS import PC_ObjectEntry, HC_ObjectEntry

from typing import List, Set
from dataclasses import dataclass, field

""" Основной класс фреймфорка"""
@dataclass
class Form:
        name: str  # имя формы уникально, столбец form.name
        comment: str = ""  # комментарий доктора о форме, столбец form.comment
        path_to_pic: str = ""  # путь к картинке-иллюстрации, приложенной доктором для наглядности, столбец form.path_to_pic
        path_to_dataset: str = "" # путь к датасету формы, столбец form.path_to_dataset

        # точки формы
        points: List[Point] = field(default_factory=list) # хранятся в таблице point, каждой точке соотв. поле point.form_id (ключ таблицы form)

        # параметры формы
        parameters: List[Parameter] = field(default_factory=list) # хранятся в таблице parameter, каждому параметру соотв. поле parameter.form_id (ключ таблицы form)

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


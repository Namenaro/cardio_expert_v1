from CORE.db_dataclasses.step import Step
from CORE.db_dataclasses.point import Point
from CORE.db_dataclasses.parameter import Parameter
from CORE.db_dataclasses.base_class import BaseClass
from CORE.db_dataclasses.base_pazzle import BasePazzle

from typing import List, Optional
from dataclasses import dataclass, field

""" Основной класс фреймфорка"""


@dataclass
class Form:
    id: Optional[int] = None  # первичный ключ в такблице form
    name: str = ""  # имя формы уникально, столбец form.name
    comment: str = ""  # комментарий доктора о форме, столбец form.comment
    path_to_pic: str = ""  # путь к картинке-иллюстрации, приложенной доктором для наглядности, столбец form.path_to_pic
    path_to_dataset: str = ""  # путь к датасету формы, столбец form.path_to_dataset

    # точки формы
    points: List[Point] = field(
        default_factory=list)  # хранятся в таблице point, каждой точке соотв. поле point.form_id (ключ таблицы form)

    # параметры формы
    parameters: List[Parameter] = field(
        default_factory=list)  # хранятся в таблице parameter, каждому параметру соотв. поле parameter.form_id (ключ таблицы form)

    # шаги установки точек формы, их столько сколько точек в форме, порядок в этом списке очень важен
    steps: List[Step] = field(default_factory=list)

    # измерители параметров проверяльщики жестких условий на параметры
    HC_PC_objects: List[BasePazzle] = field(default_factory=list)


    def is_valid(self) -> bool:
        conditions = (
            all(step.is_valid() for step in self.steps),
            len(self.steps) == len(self.points),
            len(self.parameters) > 0,
            len(self.points) > 0
        )
        return all(conditions)

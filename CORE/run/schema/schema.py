from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict, Tuple

from CORE.exeptions import SchemaError
from CORE.run.run_pazzle import PazzleParser
from CORE.run.schema.context import Context
from CORE.run.schema.schemed_HC import HC_Wrapper
from CORE.run.schema.schemed_PC import PC_Wrapper
from DA3.form_widgets.hcs_widget.HC_card import HCCard


class SchemedStep:
    def __init__(self, step: Step):
        self.step = step
        self.wPCs: List[PC_Wrapper] = []
        self.wHCs: List[HC_Wrapper] = []

    def to_text(self) -> str:
        text = f"Шаг {self.step.num_in_form} -> ставится точка {self.step.target_point.name}\n"
        "Проверяются параметры: "  # TODO

class Schema:
    """
    Класс, предназначенный для преобразования датакласса
    формы в исполняемую валидную последовательность шагов.
    При преобразовании производится порверка на валидность
    и различные логичесткие ошибкт в форме (ее "компиляция").

    Использование класса:

    Нужно оберуть Schema.run() в try/exept и если произошло падение, то
    краткие данные о проблемах формы можно извлечь из
    объекта Schema.context:Context. Из него будет понятно, на
    каком шаге формы имеются пробоемы и какие.

    Для понятного отображения итогов построения схемы (включая ошибки)
    нужно использовать метод Schema.to_text(), возвращаемый им текст удобен
    для показа пользователю в GUI

    """
    def __init__(self, form: Form):
        self.form = form
        self.context = Context()

        self.wHCs: List[HC_Wrapper] = []
        self.wPCs: List[PC_Wrapper] = []

        self.steps_sorted: List[SchemedStep] = []

    def run(self) -> None:
        """
        Основной метод.  Генерирует схему
        :return:
        """
        self._init_HC_PC()

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
            message = f"Ошибка парсинга HC|PC объектов формы {self.form.id}, " + str(e)
            self.context.add_error(message)
            raise SchemaError(message)

    def get_PCs_by_step_num(self, step_num) -> List[BasePazzle]:
        pass

    def get_HCs_by_step_num(self, step_num) -> List[BasePazzle]:
        pass

    def to_text(self) -> str:
        text = "<<< Схема выполнения формы >>>"

        # Если есть ошибки, то сначала покажем их
        if self.context.is_ok():
            text += "ФОРМА ВАЛИДНА! \n"
        else:
            text += "\n\n --- ОШИБКИ --- :"
            for err_msg in self.context.errors:
                text += err_msg + "\n"

        # Схема шагов формы (которые удалось построить до возникновения ошибки)
        text += "\n --- ШАГИ --- : \n"
        for schemed_step in self.steps_sorted:
            text += schemed_step.to_text()

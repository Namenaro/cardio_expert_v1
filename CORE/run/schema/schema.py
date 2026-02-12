from enum import Enum

from CORE.db_dataclasses import Form, Step, Point, BasePazzle, Parameter
from typing import List, Dict, Tuple

from CORE.exeptions import SchemaError
from CORE.run.run_pazzle import PazzleParser
from CORE.run.schema.context import Context
from CORE.run.schema.schemed_HC import HC_Wrapper
from CORE.run.schema.schemed_PC import PC_Wrapper
from CORE.run.schema.schemed_step import SchemedStep


class Schema:
    """
    Класс, предназначенный для преобразования датакласса
    формы в исполняемую валидную последовательность шагов.
    При преобразовании производится порверка на валидность
    и различные логичесткие ошибкт в форме (ее "компиляция").

    Использование класса:

    Нужно зупусить Schema.compile() и если вернуло False,
    краткие данные о проблемах формы можно извлечь через Schema.get_errors().

    Для понятного отображения итогов построения схемы (включая ошибки)
    нужно использовать метод Schema.to_text(), возвращаемый им текст удобен
    для показа пользователю в GUI

    """
    def __init__(self, form: Form):
        self.form = form
        self.context = Context()

        self.wHCs: List[HC_Wrapper] = []
        self.wPCs: List[PC_Wrapper] = []

        self.steps_sorted: List[SchemedStep] = [SchemedStep(step) for step in form.steps]

    def compile(self) -> bool:
        """
        Основной метод.  Генерирует схему
        :return: True если не обнаружено проблем при компиляции формы.
           Если обнаружены, то см. errors в self.context
        """
        self._init_HC_PC()

        for step in self.steps_sorted:
            # границы интервала
            sucess, absent_points = step.fit_interval(self.context)
            if not sucess:
                self.context.errors.append(f"При задании интервалане найдены точки{absent_points} ")

            # для данного шага подбираем PC и HC
            self._find_PCs_for_step(step)
            self._find_HCs_for_step(step)

            # отмечаем шаг пройденным
            self.context.add_point(step.get_step_obj().target_point.name)

        if len(self.wHCs):
            ids = [whc.hc.id for whc in self.wHCs]
            self.context.errors.append(f"Остались нераспределенные HC, id ={ids}")

        if len(self.wPCs):
            ids = [wpc.pc.id for wpc in self.wPCs]
            self.context.errors.append(f"Остались нераспределенные PC, id ={ids}")

        return self.context.is_ok()

    def _find_PCs_for_step(self, step: SchemedStep) -> None:
        """
        Заполняем список PC для данного шага при текущем контексте
        :param step: шаг, для которого вы пытаемся найти упорядоченный список PC
        :return:
        """
        PCs_list_changed = True

        while True:
            if not PCs_list_changed:
                break

            if len(self.wPCs) == 0:
                break

            # пытаемся найти ровно один PC:
            for i in range(len(self.wPCs)):
                is_ready, _, _ = self.wPCs[i].fit_context(self.context)
                if is_ready:
                    # Добавляем этот пазл в шаг
                    step.wPCs.append(self.wPCs[i])

                    # Заносим в контекст id пазла и добавленные пазлом параметры
                    self.context.add_PC(pazzle_id=self.wPCs[i].pc.id)
                    params = self.wPCs[i].returned_params()
                    map(self.context.add_param, params)

                    # Удаляем пазл из нерассмотренных
                    del self.wPCs[i]

                    # поскольку в контексте появились новые параметры,
                    # то нужно заново делать обход всех PC, т.к. даже тем из них, кому
                    # до этого момента не хватало параметров, может их тепепрь хватить
                    PCs_list_changed = True
                    break

    def _find_HCs_for_step(self, step: SchemedStep):
        """
        Заполняем список HC для данного шага при текущем контексте
        :param step: заполняемый сейчас шаг
        :return:
        """
        for i in range((len(self.wHCs) - 1), -1, -1):  # с конца, т.к. удаление по индексу в цикле
            hc = self.wHCs[i]
            is_ready, _ = hc.fit_context(self.context)
            if is_ready:
                step.wHCs.append(hc.hc.id)
                del self.wHCs[i]


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
        pcs = [wpc.pc for wpc in self.steps_sorted[step_num].wPCs]
        return pcs


    def get_HCs_by_step_num(self, step_num) -> List[BasePazzle]:
        hcs = [whc.hc for whc in self.steps_sorted[step_num].wHCs]
        return hcs

    def to_text(self) -> str:
        text = "<<< Схема выполнения формы >>>"

        # Если есть ошибки, то сначала покажем их
        if self.context.is_ok():
            text += "\n ФОРМА ВАЛИДНА!"
        else:
            text += "\n --- ОШИБКИ ---\n :"
            text += self.get_errors()

        # Схема шагов формы (которые удалось построить до возникновения ошибки)
        text += "\n --- ШАГИ --- : \n"
        for schemed_step in self.steps_sorted:
            text += schemed_step.to_text()
        return text

    def get_errors(self) -> str:
        if self.context.is_ok():
            return "Ошибок нет"

        current_num_step = self.context.nums_of_steps_done[-1] if self.context.nums_of_steps_done else 0
        err_info = f" При выполнеии {current_num_step} шага ошибки: \n {'\n'.join(self.context.errors)}"
        return err_info

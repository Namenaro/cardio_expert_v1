from typing import List

from CORE import Signal
from CORE.db_dataclasses import Form, Step, Point, BasePazzle
from CORE.exeptions import FormError
from CORE.run import Exemplar
from CORE.run.r_hc import R_HC
from CORE.run.r_pc import R_PC
from CORE.run.r_step import RStep
from CORE.run.r_track import RTrack
from CORE.run.schema import Schema
from CORE.run.step_interval import Interval


class RStepsListCreator:
    """
    Класс, который на основе датакласса формы конструирует
    запускаемые объекты шагов ее выполнения, заодно проверяя внутреннюю
    согласованность датакласса, полученнного десериализацией формы из
    базы данных форм
     """

    def from_db_form(self, form: Form, schema: Schema) -> List[RStep]:
        """
        :raises SchemaError, FormError
        :param form: датакласс формы, на  основе которого конструкируем этот
        :param schema: схема, по которой заполняем запускабельные шаги
        :return: self
        """
        self.form = form

        # Инициализуирем шаги
        self.rsteps: List[RStep] = []
        for step_bd in form.steps:
            r_step = self._init_rstep(step_bd, schema)
            self.rsteps.append(r_step)
        return self.rsteps

    def _init_rstep(self, step: Step, schema: Schema):
        """
        Создание одного запускаемого объекта шага на основе датакласса шага
        :param step: датакласс шага
        :param schema: Схема пошагового запуска формы
        :return:
        :raises FormError
        """

        # 1. Извлекаем интервал
        interval = self._get_interval_for_step(step)

        # 2. Извлекаем треки
        r_tracks = [RTrack(track=track) for track in step.tracks]

        PC_objects_for_step = schema.get_PCs_by_step_num(step_num=step.num_in_form)
        rPC_objects = [R_PC(pc_pazzle, form_points=self.form.points,
                            form_params=self.form.parameters)
                       for pc_pazzle in PC_objects_for_step
                       ]

        # 3. Излекаем HC\PC согласно схеме
        HC_objects_for_step = schema.get_HCs_by_step_num(step_num=step.num_in_form)
        rHC_objects = [R_HC(hc_pazzle, form_params=self.form.parameters)
                       for hc_pazzle in HC_objects_for_step
                       ]

        # 4. Собираем все это в запускаемый объект шага
        rstep = RStep(interval=interval,
                      r_tracks=r_tracks,
                      target_point_name=step.target_point.name,
                      num_in_form=step.num_in_form,
                      center=None,  # это можно получить только в рантайме
                      rPC_objects=rPC_objects,
                      rHC_objects=rHC_objects
                      )
        return rstep

    def _get_interval_for_step(self, step: Step) -> Interval:
        """
        :raises FormError
        :param step: объект шага
        :return: объект интервал для этого шага
        """
        try:
            interval = Interval()
            # Правое ограничение (имя точки или размер отступа)
            if step.right_point:
                interval.set_point_right(step.right_point.name)
            else:
                interval.set_right_padding(step.right_padding_t)

            # Левое ограничение (имя точки или размер отступа)
            if step.left_point:
                interval.set_point_left(step.left_point.name)
            else:
                interval.set_left_padding(step.left_padding_t)

            return interval
        except Exception as e:
            raise FormError.invalid_interval_deserialised(form_id=self.form.id,
                                                          step_num=step.num_in_form,
                                                          error=str(e))

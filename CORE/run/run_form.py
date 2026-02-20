from typing import List

from CORE import Signal
from CORE.db_dataclasses import Form
from CORE.exeptions import SchemaError
from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.run.r_steps_creator import RStepsListCreator
from CORE.run.r_step import RStep
from CORE.run.schema import Schema


class RunForm:
    """
    Основной класс, экспортируемый библиотекой устновщика форм - запускает устновку формы на одномерном сигнале, и выдает несколько вариантов ее установки
    """

    def __init__(self, form: Form, max_pool_size: int = 5):
        form = form
        self.max_pool_size = max_pool_size

        schema = Schema(form)
        sucess = schema.compile()
        if not sucess:
            raise SchemaError

        self.rsteps: List[RStep] = RStepsListCreator().from_db_form(form, schema)

    def run(self, big_signal: Signal, seminal_point: float) -> ExemplarsPool:
        """
        Внутри формы точки пронумерованы и для каждой задано ограничение слева и справа для интервала поиска экземпляра этой точки.
        Таким образом, первая точка имеет связанный с ней интервал ее поиска.

        seminal_point интерпретируем как задание "центра" этого интевала.
        "Центр" в кавыычках, потому что для точки формы интервал хранится ввиде "отстсуп влево", "отствуп вправо". Они не обязаны быть симметричныи.

        Для внутренних точек формы границами интервала ее поиска выступают зачастую другие точки, но для первой точки формы интервалы всегда заданы в базе данных числами.

        :param big_signal: это сигнал, на котором (с запасом) должен уместиться итоговый экземпляр формы
        :param seminal_point: это кордината во времени (секунды), куда мы "ориентировочно" кидаем первую точку формы
        :return: набор экземпляров
        """
        initial_exemplar = Exemplar(signal=big_signal)
        exemplars_pool = ExemplarsPool(signal=big_signal, max_size=self.max_pool_size)
        exemplars_pool.add_exemplar(initial_exemplar)

        self.rsteps[0].set_step_as_first(seminal_point)

        for rstep in self.rsteps:
            # на основе прошлого пула "недорощенных" экземпляров составляем новый пул - в нем экземпляры на одну точку длиннее
            new_pool = ExemplarsPool(signal=big_signal, max_size=self.max_pool_size)

            for parent_exemplar in exemplars_pool:
                # каждый старый экземпляр дает несколько дочерних
                exemplars = rstep.run(parent_exemplar)

                # все дочерние экземпляры от всех старых экземпляров собираем воедино
                for exemplar in exemplars:
                    new_pool.add_exemplar(exemplar)

            exemplars_pool = new_pool

        return exemplars_pool

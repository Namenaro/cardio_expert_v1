from typing import List, Tuple, Optional

from CORE import Signal
from CORE.db_dataclasses import Form
from CORE.exeptions import SchemaError
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.run.r_step import RStep
from CORE.run.r_steps_creator import RStepsListCreator
from CORE.run.schema import Schema


class RForm:
    """
    Основной класс, экспортируемый библиотекой установщика форм - запускает установку формы на одномерном сигнале, и выдает несколько вариантов ее установки
    """

    def __init__(self, form: Form, evaluator: BaseEvaluator, max_pool_size: int = 5):
        self.form = form
        self.schema = Schema(form)  # сохраняем схему
        sucess = self.schema.compile()
        if not sucess:
            raise SchemaError

        self.max_pool_size = max_pool_size
        self.evaluator = evaluator

        self.rsteps: List[RStep] = RStepsListCreator().from_db_form(form, self.schema)

    def run(self, big_signal: Signal, seminal_point: float) -> ExemplarsPool:
        """
        Внутри формы точки пронумерованы и для каждой задано ограничение слева и справа для интервала поиска экземпляра этой точки.
        Таким образом, первая точка имеет связанный с ней интервал ее поиска.

        seminal_point интерпретируем как задание "центра" этого интервала.
        "Центр" в кавычках, потому что для точки формы интервал хранится в виде "отступ влево", "отступ вправо". Они не обязаны быть симметричны.

        Для внутренних точек формы границами интервала ее поиска выступают зачастую другие точки, но для первой точки формы интервалы всегда заданы в базе данных числами.

        :param big_signal: это сигнал, на котором (с запасом) должен уместиться итоговый экземпляр формы
        :param seminal_point: это координата во времени (секунды), куда мы "ориентировочно" кидаем первую точку формы
        :return: набор экземпляров
        """
        initial_exemplar = Exemplar(signal=big_signal)
        initial_exemplar.evaluation_result = 0.0
        exemplars_pool = ExemplarsPool(signal=big_signal, max_size=self.max_pool_size)
        exemplars_pool.add_exemplar(initial_exemplar)

        self.rsteps[0].set_step_as_first(seminal_point)

        for rstep in self.rsteps:
            # на основе прошлого пула "недорощенных" экземпляров составляем новый пул - в нем экземпляры на одну точку длиннее
            new_pool = ExemplarsPool(signal=big_signal, max_size=self.max_pool_size)

            for parent_exemplar in exemplars_pool:
                # каждый старый экземпляр дает несколько дочерних
                # Игнорируем StepRes, так как он не нужен для текущей логики
                _, exemplars = rstep.run(parent_exemplar)

                # все дочерние экземпляры от всех старых экземпляров собираем воедино
                for exemplar in exemplars:
                    exemplar.evaluation_result = self.evaluator.eval_exemplar(exemplar)
                    new_pool.add_exemplar(exemplar)

            exemplars_pool = new_pool

        return exemplars_pool

    def find_track_by_sm_id(self, sm_id: int) -> Optional[Tuple[int, int]]:
        """
        Находит трек, содержащий SM с указанным ID.

        Args:
            sm_id: ID SM-пазла в базе

        Returns:
            Optional[Tuple[int, int]]: (индекс_шага, track_id) или None, если не найден
        """
        for step_idx, rstep in enumerate(self.rsteps):
            for track in rstep.r_tracks:
                for sm in track.rSM_objects:
                    if sm.base_pazzle.id == sm_id:
                        return step_idx, track.id
        return None

    def find_track_by_ps_id(self, ps_id: int) -> Optional[Tuple[int, int]]:
        """
        Находит трек, содержащий PS с указанным ID.

        Args:
            ps_id: ID PS-пазла в базе

        Returns:
            Optional[Tuple[int, int]]: (индекс_шага, track_id) или None, если не найден
        """
        for step_idx, rstep in enumerate(self.rsteps):
            for track in rstep.r_tracks:
                for ps in track.rPS_objects:
                    if ps.base_pazzle.id == ps_id:
                        return step_idx, track.id
        return None

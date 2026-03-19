from typing import List, Optional, Union

from CORE.db_dataclasses import Form, BasePazzle
from CORE.exeptions import SchemaError, PazzleOutOfSignal
from CORE.run import Exemplar
from CORE.run.r_hc import R_HC
from CORE.run.r_pc import R_PC
from CORE.run.schema import Schema
from CORE.logger import get_logger

logger = get_logger(__name__)


class Parametriser:
    """ Класс для применения объектов HC|PC к экземпляру, у которого уже заполнены все точки"""

    def __init__(self, form: Optional[Form] = None, schema: Optional[Schema] = None):
        """
        :param form: форма (опционально)
        :param schema: готовая схема (опционально)
        Должно быть передано ровно одно из двух: form или schema
        """
        if form is None and schema is None:
            raise ValueError("Должен быть передан либо form, либо schema")

        if form is not None and schema is not None:
            raise ValueError("Нельзя передавать одновременно form и schema")

        if form is not None:
            self.form = form
            self.schema = Schema(form)
            if not self.schema.compile():
                raise SchemaError
        else:
            self.schema = schema
            self.form = schema.form

    def _create_r_pcs_for_step(self, step_num: int) -> List[R_PC]:
        """Создает R_PC объекты для указанного шага по схеме"""
        base_pazzles = self.schema.get_PCs_by_step_num(step_num)
        return [R_PC(base_pazzle=pc, form_points=self.form.points, form_params=self.form.parameters)
                for pc in base_pazzles]

    def _create_r_hcs(self) -> List[R_HC]:
        """Создает R_HC объекты из HC_PC_objects формы"""
        return [R_HC(pazzle, form_params=self.form.parameters)
                for pazzle in self.form.HC_PC_objects if pazzle.is_HC()]

    def _apply_r_pcs(self, exemplar: Exemplar, r_pcs: List[R_PC]) -> None:
        """Применяет список R_PC к экземпляру"""
        for r_pc in r_pcs:
            measured_new_params = r_pc.run(exemplar)
            for param_name, param_value in measured_new_params.items():
                exemplar.add_parameter(param_name, param_value=param_value)

    def _apply_r_hcs(self, exemplar: Exemplar, r_hcs: List[R_HC]) -> bool:
        """Применяет список R_HC к экземпляру и возвращает результат проверки"""
        exemplar.passed_HCs_ids = []
        exemplar.failed_HCs_ids = []

        all_fitted = True
        for r_hc in r_hcs:
            fitted = r_hc.run(exemplar)
            if fitted:
                exemplar.passed_HCs_ids.append(r_hc.base_pazzle.id)
            else:
                exemplar.failed_HCs_ids.append(r_hc.base_pazzle.id)
                all_fitted = False

        return all_fitted

    def parametrise_from_form(self, exemplar: Exemplar, form: Form) -> None:
        """
        Считая, что у экземпляра заполнены все точки, измерить и внести в него все параметры
        :param exemplar: экземпляр, в котором будут измеряться параметры
        :param form: форма для этого экземпляра
        :raises RunPazzleError, PazzleOutOfSignal
        """
        # Последовательность применения PC важна, поэтому берем порядок их применения, уже расчитанный в схеме
        for step_num in range(len(form.steps)):
            r_pcs = self._create_r_pcs_for_step(step_num)
            self._apply_r_pcs(exemplar, r_pcs)

    def parametrise(self, exemplar: Exemplar, r_pcs: List[R_PC]) -> None:
        """
        Параметризует экземпляр, используя готовые объекты R_PC.
        :param exemplar: экземпляр для параметризации
        :param r_pcs: список готовых объектов R_PC
        :raises PazzleOutOfSignal, RunPazzleError
        """
        self._apply_r_pcs(exemplar, r_pcs)

    def check_HCs_from_form(self, exemplar: Exemplar, form: Form) -> bool:
        """
        Считая, что у данного экземпляра заполнене все параметры, проверят жесткие условия.
        Заполняет список id проваленных/выполненных жесткий условий, записывает его в данный экземпляр
        :param form: форма, из которой берется список жсетких условий
        :raises RunPazzleError
        :return: true если все условия формы выполнились
        """
        r_hcs = self._create_r_hcs()
        return self._apply_r_hcs(exemplar, r_hcs)

    def fit_conditions(self, exemplar: Exemplar, r_hcs: List[R_HC]) -> bool:
        """
        Проверяет жесткие условия на экземпляре, используя готовые объекты R_HC.
        :param exemplar: экземпляр для проверки
        :param r_hcs: список готовых объектов R_HC
        :raises RunPazzleError
        :return: True если все условия выполнены
        """
        return self._apply_r_hcs(exemplar, r_hcs)

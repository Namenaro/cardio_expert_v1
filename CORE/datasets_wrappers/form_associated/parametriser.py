from typing import List

from CORE.db_dataclasses import Form, BasePazzle
from CORE.exeptions import SchemaError
from CORE.run import Exemplar
from CORE.run.r_hc import R_HC
from CORE.run.r_pc import R_PC
from CORE.run.schema import Schema


class Parametriser:
    """ Класс для применения объектов HC|PC к экземпляру, у которого уже заполнены все точки"""

    @classmethod
    def parametrise_from_form(self, exemplar: Exemplar, form: Form) -> None:
        """
        Считая, что у экземпляра заполнены все точки, измерить и внести в него все параметры
        :param exemplar: экземпляр, в котором будут измеряться параметры
        :param form: форма для этого экземпляра
        :raises RunPazzleError, PazzleOutOfSignal
        :return:
        """
        schema = Schema(form)
        if not schema.compile():
            raise SchemaError

        # Последовательность расчета PC берем из схемы
        for step_num in range(len(form)):
            baze_pazzles_pc: List[BasePazzle] = schema.get_PCs_by_step_num(step_num)
            r_pcs = [R_PC(base_pazzle=pc, form_points=form.points, form_params=form.parameters) for pc in
                     baze_pazzles_pc]

            for r_pc in r_pcs:
                measured_new_params = r_pc.run(exemplar)
                for param_name, param_value in measured_new_params.items():
                    exemplar.add_parameter(param_name, param_value=param_value)

    @classmethod
    def check_HCs_from_form(self, exemplar: Exemplar, form: Form) -> bool:
        """
        Считая, что у данного экземпляра заполнене все параметры, проверят жесткие условия.
        Заполняет список id проваленных/выполненных жесткий условий, записывает его в данный экземпляр
        :param form: форма, из которой берется список жсетких условий
        :raises RunPazzleError
        :return: true если все условия формы выполнились
        """
        r_hcs = [R_HC(pazzle, form_params=form.parameters) for pazzle in form.HC_PC_objects if pazzle.is_HC()]
        for r_hc in r_hcs:
            fitted = r_hc.run(exemplar)
            if fitted:
                exemplar.passed_PCs_ids.append(r_hc.id)
            else:
                exemplar.failed_PCs_ids.append(r_hc.id)
        all_fitted = len(exemplar.failed_PCs_ids) == 0
        return all_fitted

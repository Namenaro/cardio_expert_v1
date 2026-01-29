from typing import List

from CORE.db_dataclasses import Form
from CORE.run import Exemplar
from CORE.run.r_hc import R_HC
from CORE.run.r_pc import R_PC


class Parametriser:
    """ Класс для применения объектов HC|PC к экземпляру"""

    def parametrise(self, exemplar: Exemplar, r_pcs: List[R_PC]):
        """
        По очереди (порядок важен) примеряет обънкты вида PC к данному экземпляру.
        Результаты расчета записываются в текущий экземпляр.
        :param r_pcs:
        :return:
        """
        for r_pc in r_pcs:
            measured_new_params = r_pc.run(exemplar)
            for param_name, param_value in measured_new_params.items():
                exemplar.add_parameter(param_name, param_value=param_value)

    def fit_conditions(self, exemplar: Exemplar, r_hcs: List[R_HC]) -> bool:
        """
        Применяет список жестких условий к экземпляру. При этому в экзепрляр
        производится дозапись информации о том, какие условия выполнены и какие провалены.
        :param exemplar:
        :param r_hcs:
        :return:
        """
        for r_hc in r_hcs:
            fitted = r_hc.run(exemplar)
            if fitted:
                exemplar.passed_PCs_ids.append(r_hc.id)
            else:
                exemplar.failed_PCs_ids.append(r_hc.id)
        return len(exemplar.failed_PCs_ids) == 0

    def parametrise_from_form(self, exemplar: Exemplar, form: Form) -> None:
        """
        Считая, что у экземпляра заполнены все точки, измерить и внести в него все параметры
        :param exemplar: экземпляр, в котором будут измеряться параметры
        :param form: форма для этого экземпляра
        :return:
        """
        r_pcs = [
            R_PC(base_pazzle=pc, form_points=form.points, form_params=form.parameters)
            for pc in form.HC_PC_objects
            if pc.is_PC()
        ]
        assert len(r_pcs) > 0, "Форма не содержит параметризаторов, должен быть хотя бы один"
        self.parametrise(exemplar, r_pcs=r_pcs)

    def check_HCs_from_form(self, exemplar: Exemplar, form: Form) -> bool:
        """
        Считая, что у данного экземпляра заполнене все параметры, проверят жесткие условия.
        Заполняет список id проваленных/выполненных жесткий условий, записывает его в данный экземпляр
        :param form: форма, из которой берется список жсетких условий
        :return: true если все условия формы выполнились
        """
        r_hcs = [R_HC(pazzle, form_params=form.parameters) for pazzle in form.HC_PC_objects if pazzle.is_HC()]
        return self.fit_conditions(exemplar, r_hcs=r_hcs)

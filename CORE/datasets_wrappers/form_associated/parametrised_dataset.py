from typing import List, Any

import pandas as pd

from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.datasets_wrappers.form_associated.parametriser import Parametriser
from CORE.db_dataclasses import Form
from CORE.exeptions import CoreError


class ParametrisedDataset:
    """
    Формирует две пандас-таблицы. Одна содержит
    датасет параметров, вторая датасет нарушенных HC.
    Обе индексируются id экземпляра из соответствующего "сырого" датасета экземпляров
    """

    # Константа для имени колонки с идентификатором экземпляра
    ID_COLUMN = 'id_exemplar'

    def __init__(self, raw_exemplars: ExemplarsDataset, form: Form):
        # Имена столбцов для обеих таблиц берем из спецификации формы
        self.param_names = [param.name for param in form.parameters]
        assert len(self.param_names) > 0, f"Форма {form.id} не содержит параметров"
        self.hc_ids = [str(hc.id) for hc in form.HC_PC_objects if hc.is_HC()]

        # Таблица значений параметров для каждого экземпляра
        params_names = [self.ID_COLUMN] + self.param_names
        self.parameters_frame = pd.DataFrame(columns=params_names)
        self.parameters_frame.attrs[
            'raw_name'] = raw_exemplars.form_dataset_name if raw_exemplars.form_dataset_name is not None else "unknown"

        # Таблица id-ов нарушенных жестких условий для каждого экземпляра
        violations_columns = [self.ID_COLUMN] + [str(hc_id) for hc_id in self.hc_ids]
        self.violations_frame = pd.DataFrame(columns=violations_columns)

        # Заполняем обе таблицы
        self.fill_frames(raw_exemplars, form)

    def fill_frames(self, raw_exemplars: ExemplarsDataset, form: Form) -> None:
        exemplar_parametriser = Parametriser(form)

        # Собираем данные для обоих фреймов
        parameters_data = []
        violations_data = []

        for exemplar_id, exemplar in raw_exemplars.exemplars.items():
            # Параметризуем экземпляр
            exemplar_parametriser.parametrise_from_form(exemplar, form)
            exemplar_parametriser.check_HCs_from_form(exemplar, form)

            # Строка для таблицы параметров
            param_row = {self.ID_COLUMN: exemplar_id}
            param_row.update(exemplar._parameters)
            parameters_data.append(param_row)

            # Строка для таблицы нарушений
            viol_row = {self.ID_COLUMN: exemplar_id}
            for hc_id in self.hc_ids:
                viol_row[hc_id] = hc_id in [str(id) for id in exemplar.failed_HCs_ids]
            violations_data.append(viol_row)

        # Создаем фреймы из собранных данных
        if parameters_data:
            self.parameters_frame = pd.DataFrame(parameters_data)
        if violations_data:
            self.violations_frame = pd.DataFrame(violations_data)

    def get_exemplar_ids_violated(self) -> List[Any]:
        """
        Возвращает список id экземпляров, у которых есть хотя бы одно нарушение HC

        :returns List[Any]: список id экземпляров с нарушениями
        """
        if self.violations_frame.empty:
            return []

        # Выбираем только колонки с HC (все кроме id_exemplar)
        hc_columns = [col for col in self.violations_frame.columns if col != self.ID_COLUMN]

        # Находим строки, где хотя бы один HC равен True
        violated_mask = self.violations_frame[hc_columns].any(axis=1)

        # Возвращаем соответствующие id
        return self.violations_frame.loc[violated_mask, self.ID_COLUMN].tolist()

    def get_exemplars_by_hc_id(self, hc_id: str) -> List[Any]:
        """
        Возвращает список id экземпляров, у которых нарушено указанное HC

        :param hc_id: идентификатор жесткого условия
        :return List[Any]: список id экземпляров с нарушением данного HC
        """
        if self.violations_frame.empty:
            return []

        str_hc_id = str(hc_id)
        if str_hc_id not in self.violations_frame.columns:
            return []

        # Находим строки, где указанный HC равен True
        violated_mask = self.violations_frame[str_hc_id] == True

        # Возвращаем соответствующие id
        return self.violations_frame.loc[violated_mask, self.ID_COLUMN].tolist()


def get_parameter_values(self, param_name: str) -> List[Any]:
    """
    Возвращает список значений указанного параметра для всех экземпляров
    :param: param_name имя параметра
    :return List[Any]: список значений параметра
    """
    if self.parameters_frame.empty or param_name not in self.parameters_frame.columns:
        raise CoreError(
            f"Из датасета параметров запрошен несуществующий параметр {param_name}, исходная форма содержит параметры: {self.param_names}")

    # Возвращаем значения параметра в виде списка (без индексов)
    return self.parameters_frame[param_name].tolist()

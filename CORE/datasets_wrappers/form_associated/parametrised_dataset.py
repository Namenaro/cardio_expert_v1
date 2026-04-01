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
    # Префикс для колонок с жесткими условиями
    HC_PREFIX = 'HC_'

    def __init__(self, raw_exemplars: ExemplarsDataset, form: Form):
        # Имена столбцов для обеих таблиц берем из спецификации формы
        self.param_names = [param.name for param in form.parameters]
        assert len(self.param_names) > 0, f"Форма {form.id} не содержит параметров"
        # Добавляем префикс HC_ к названиям колонок
        self.hc_ids = [f"{self.HC_PREFIX}{hc.id}" for hc in form.HC_PC_objects if hc.is_HC()]

        # Таблица значений параметров для каждого экземпляра
        params_names = [self.ID_COLUMN] + self.param_names
        self.parameters_frame = pd.DataFrame(columns=params_names)
        self.parameters_frame.attrs[
            'raw_name'] = raw_exemplars.form_dataset_name if raw_exemplars.form_dataset_name is not None else "unknown"

        # Таблица id-ов нарушенных жестких условий для каждого экземпляра
        violations_columns = [self.ID_COLUMN] + self.hc_ids
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
                # Убираем префикс для поиска в exemplar.failed_HCs_ids
                original_hc_id = hc_id.replace(self.HC_PREFIX, '')
                viol_row[hc_id] = original_hc_id in [str(id) for id in exemplar.failed_HCs_ids]
            violations_data.append(viol_row)

        # Создаем фреймы из собранных данных
        if parameters_data:
            self.parameters_frame = pd.DataFrame(parameters_data)
        if violations_data:
            self.violations_frame = pd.DataFrame(violations_data)

    def get_merged_frame(self) -> pd.DataFrame:
        """
        Возвращает объединенный фрейм, содержащий параметры и информацию о нарушении HC

        Объединяет parameters_frame и violations_frame по id_exemplar.
        Для HC колонок значения True/False преобразуются в "нарушено"/"не нарушено"
        для удобства отображения.

        Returns:
            pd.DataFrame: объединенный фрейм
        """
        if self.parameters_frame.empty:
            return pd.DataFrame()

        # Начинаем с фрейма параметров
        merged_df = self.parameters_frame.copy()

        # Если есть фрейм нарушений, объединяем их
        if not self.violations_frame.empty:
            # Объединяем по id_exemplar (левый join, чтобы сохранить все записи)
            merged_df = pd.merge(
                merged_df,
                self.violations_frame,
                on=self.ID_COLUMN,
                how='left'
            )

            # Преобразуем булевы значения в читаемый текст для HC колонок
            hc_columns = [col for col in self.violations_frame.columns if col != self.ID_COLUMN]
            for hc_col in hc_columns:
                if hc_col in merged_df.columns:
                    merged_df[hc_col] = merged_df[hc_col].map({
                        True: "нарушено",
                        False: "не нарушено",
                        pd.NA: "не нарушено"
                    }).fillna("не нарушено")

        return merged_df

    # ... остальные методы остаются без изменений

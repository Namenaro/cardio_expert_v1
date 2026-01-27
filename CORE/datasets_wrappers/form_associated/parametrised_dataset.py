from pathlib import Path
from typing import Optional

import pandas as pd

from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.db_dataclasses import Form
from CORE.run.parametriser import Parametriser
from CORE.run.run_form import RunForm


class ParametrisedDataset:
    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        Базовый конструктор. Для создания объекта используйте classmethod-ы.
        """
        self.data = data

    @classmethod
    def from_file(cls, filepath: str):
        """
        Создаёт экземпляр себя из файла.

        Args:
            filepath (str): путь к файлу с данными ( .parquet)

        Returns:
            ParametrisedDataset: новый экземпляр класса
        """
        path = Path(filepath)

        if path.suffix == '.parquet':
            data = pd.read_parquet(path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {path.suffix}")
        return cls(data)

    @classmethod
    def from_raw_dataset(cls, raw_exemplars: ExemplarsDataset, parametriser: Parametriser):
        """
        Создаёт экземпляр ParametrisedDataset на основе объекта датасета экземпляров
        """

        rows = []

        for exemplar_id, exemplar in raw_exemplars._exemplars.items():
            # Первый столбец таблицы это id записи непараметризованного (сыорго датасета)
            row = {'id': exemplar_id}

            # В сыром датасете параметры экзепляра не посчитаны, но расставлены все точки. На их основе заполяем параметры
            parametriser.parametrise_exemplar(exemplar)

            # Добавляем все параметры из _parameters экземпляра Exemplar в строку таблицы
            for param_name, param_value in exemplar._parameters.items():
                row[param_name] = param_value

            rows.append(row)

        # Создаём DataFrame
        data = pd.DataFrame(rows)

        # Сохраняем метаинформацию в attrs
        data.attrs[
            'raw_name'] = raw_exemplars.form_dataset_name if raw_exemplars.form_dataset_name is not None else "unknown"

        return cls(data)

    def save_to_file(self, filename: str):
        """
            Сохраняет себя в файл

            Args:
                filename (str): имя файла с указанием формата .parquet
            """
        path = Path(filename)

        if path.suffix == '.parquet':
            self.data.to_parquet(path, engine='pyarrow')
        else:
            raise ValueError(
                f"Неподдерживаемый формат для сохранения парамертризованного датасета формы: {path.suffix}")

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import numpy as np

from CORE.run import Exemplar


class BaseEvaluator(ABC):
    """ Базовый класс для оценщиков"""

    @abstractmethod
    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Посчитать оценку того, насколько "вероятно", что данный экземпляр действительно является экземпляром данной формы.
        :param exemplar: оцениваемый экземпляр формы. Возможно, заполненный лишь частично.
        :return: оценка из интервала [0;1], интерпретируемая как правдоподобие, уверенность (выше - лучше).
        """
        pass

    def _get_common_data(self, exemplar: Exemplar, dataset_param_names: List[str], positive_dataset) -> Tuple[
        Optional[np.ndarray], Optional[np.ndarray], List[str]]:
        """
        Возвращает кортеж из вектора значений экземпляра и матрицы данных из датасета для общих параметров.
        Порядок колонок в обоих случаях одинаковый и соответствует порядку параметров в dataset_param_names.

        :param exemplar: оцениваемый экземпляр
        :param dataset_param_names: список имен параметров из датасета в определенном порядке
        :param positive_dataset: датасет с данными
        :return: (vector, matrix, common_params) где:
                 - vector: numpy массив формы (1, len(common_params)) или None, если общих параметров нет
                 - matrix: numpy массив формы (n_samples, len(common_params)) или None, если общих параметров нет
                 - common_params: список общих имен параметров в том же порядке, что и в dataset_param_names
        """
        # Находим общие параметры, сохраняя порядок из dataset_param_names
        dataset_params_set = set(dataset_param_names)
        exemplar_params_set = set(exemplar.get_param_names())

        # Сохраняем порядок из dataset_param_names
        common_params = [p for p in dataset_param_names if p in exemplar_params_set]

        # Если нет общих параметров, возвращаем None
        if not common_params:
            return None, None, []

        # Формируем вектор значений из экземпляра
        vector = np.array([[
            exemplar.get_parameter_value(p) for p in common_params
        ]])

        # Формируем матрицу данных из датасета
        data_list = [positive_dataset.get_parameter_values(p) for p in common_params]
        matrix = np.array(data_list).T

        return vector, matrix, common_params

from typing import Dict, List
import scipy.stats as stats

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.eval import BaseEvaluator
from abc import ABC, abstractmethod


class MannWhitneyEval(BaseEvaluator):
    """Оценка экземпляра через критерий Манна‑Уитни: чем выше значение, тем больше похожесть на выборку.

    Для каждого параметра оцениваемого экземпляра:
       - формируется вторая выборка, состоящая из одного значения — `real_value` (значение параметра в экземпляре);
       - применяется критерий Манна‑Уитни для сравнения двух выборок: эталонной позитивной и одноэлементной;
       - получается p‑значение — вероятность того, что выборки происходят из одного распределения;
       - p‑значение преобразуется в оценку похожести: `score = 1.0 - p_value`.
       """

    def __init__(self, positive_dataset: ParametrisedDataset):
        """Инициализирует объект, сохраняя значения параметров из позитивного датасета."""
        self.param_to_values: Dict[str, List[float]] = {}
        for param in positive_dataset.param_names:
            vals: List[float] = positive_dataset.get_parameter_values(param)
            self.param_to_values[param] = vals

    def _eval_one_param(self, param_name: str, real_value: float) -> float:
        """Вычисляет оценку похожести одного параметра на выборку (чем выше, тем лучше)."""
        vals = self.param_to_values.get(param_name)
        if vals is None:
            raise ValueError(f"Parameter '{param_name}' not found in training data.")

        sample_a = vals  # Выборка из позитивного датасета
        sample_b = [real_value]  # Значение из экземпляра

        try:
            _, p_value = stats.mannwhitneyu(
                sample_a, sample_b,
                alternative='two-sided',
                method='auto'
            )
        except ValueError as e:
            if 'All numbers are identical' in str(e):
                p_value = 1.0  # Максимальная похожесть
            else:
                raise e

        # Преобразуем p‑значение: чем ближе к 1, тем выше оценка
        score = 1.0 - p_value
        return score

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """Возвращает итоговую оценку экземпляра: сумма оценок по параметрам, нормализованная на их количество."""
        scores = []
        params_names = exemplar.get_param_names()

        for param_name in params_names:
            real_val = exemplar.get_parameter_value(param_name)
            score = self._eval_one_param(param_name, real_val)
            scores.append(score)

        if not scores:
            return 0.0

        # Нормализуем: среднее по всем параметрам → значение в [0;1]
        avg_score = sum(scores) / len(scores)
        return 1 - avg_score


if __name__ == "__main__":
    from unittest.mock import Mock
    import numpy as np

    # Создаём mock для ParametrisedDataset
    mock_dataset = Mock()
    mock_dataset.param_names = ['param1', 'param2', 'param3']

    # Генерируем более реалистичные данные с шумом
    np.random.seed(42)
    n_samples = 50

    # Базовая структура с корреляцией, но не идеальной
    param1 = np.random.normal(3, 1, n_samples)
    param2 = 2 * param1 + np.random.normal(0, 0.5, n_samples)  # корреляция с шумом
    param3 = 0.5 * param1 + np.random.normal(0, 0.2, n_samples)  # корреляция с шумом

    test_data = {
        'param1': param1.tolist(),
        'param2': param2.tolist(),
        'param3': param3.tolist()
    }


    def mock_get_parameter_values(param_name):
        return test_data[param_name]


    mock_dataset.get_parameter_values.side_effect = mock_get_parameter_values

    # Создаём mock для Exemplar
    mock_exemplar = Mock()

    # Инициализируем оценщик
    evaluator = MannWhitneyEval(mock_dataset)

    # Тест 1: Нормальный экземпляр (в центре распределения)
    normal_values = {
        'param1': 3.0,  # среднее
        'param2': 6.0,  # среднее (примерно)
        'param3': 1.5  # среднее (примерно)
    }


    def mock_normal_get_value(param_name):
        return normal_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_normal_get_value
    mock_exemplar.get_param_names.return_value = ['param1', 'param2', 'param3']

    normal_score = evaluator.eval_exemplar(mock_exemplar)
    print(f"\nОценка нормального экземпляра: {normal_score:.4f}")

    # Тест 2: Слегка отклоняющийся экземпляр
    mild_values = {
        'param1': 4.0,
        'param2': 7.5,
        'param3': 2.2
    }


    def mock_mild_get_value(param_name):
        return mild_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_mild_get_value

    mild_score = evaluator.eval_exemplar(mock_exemplar)
    print(f"Оценка слегка отклоняющегося: {mild_score:.4f}")

    # Тест 3: Выброс
    outlier_values = {
        'param1': 10.0,
        'param2': -5.0,
        'param3': 5.0
    }


    def mock_outlier_get_value(param_name):
        return outlier_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_outlier_get_value

    outlier_score = evaluator.eval_exemplar(mock_exemplar)
    print(f"Оценка выброса: {outlier_score:.4f}")

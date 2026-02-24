from typing import Dict, List
import scipy.stats as stats

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.eval import BaseEvaluator
from abc import ABC, abstractmethod


class MannWhitneyEval(BaseEvaluator):
    """Оценка экземпляра через критерий Манна‑Уитни: чем выше значение, тем больше похожесть на выборку.

    Для каждого параметра оцениваемого экземпляра (`Exemplar`):
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
        return avg_score

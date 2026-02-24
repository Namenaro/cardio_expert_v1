from dataclasses import dataclass
from statistics import mean, stdev
from typing import Optional, Dict, List

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.eval import BaseEvaluator

class SumDistsEval(BaseEvaluator):
    """
    Оценка экземпляра через нормированные отклонения параметров от матожидания позитивной выборки.

    1. Для каждого параметра из позитивной выборки (`ParametrisedDataset`) вычисляются:
       - матожидание (`mu`) — среднее значение параметра в позитивной выборке;
       - стандартное отклонение (`sigma`) — мера разброса значений параметра.

    2. Для каждого параметра оцениваемого экземпляра (`Exemplar`):
       - вычисляется нормированное отклонение его значения от `mu`: `|real_value - mu| / sigma` (при `sigma = 0` отклонение считается нулевым);
       - нормированное отклонение преобразуется в оценку похожести по формуле
       `1.0 / (1.0 + normalized_deviation)` — это обеспечивает плавное нелинейное убывание оценки
       от 1.0 (полное совпадение) к значениям, близким к 0.0 (сильное отклонение).

    3. Итоговая оценка экземпляра — среднее арифметическое оценок по всем его параметрам. Результат находится в интервале [0; 1], где:
       - 1.0 означает максимальную похожесть на позитивную выборку;
       - 0.0 указывает на сильное отклонение от неё.

    Ограничения:

    * При наличии выбросов в позитивной выборке `sigma` может быть завышенным
    * Для малых выборок (`n < 30`) оценки могут быть менее стабильными.
    * Полагаем, что распределение близко к нормальному
    """

    @dataclass
    class MuSigma:
        mu: Optional[float] = None
        sigma: Optional[float] = None

    def __init__(self, positive_dataset: ParametrisedDataset):
        """Инициализирует объект, вычисляя mu и sigma для всех параметров из позитивного датасета."""
        self.param_to_mu_sigma: Dict[str, SumDistsEval.MuSigma] = {}
        for param in positive_dataset.param_names:
            vals: List[float] = positive_dataset.get_parameter_values(param)
            mu = mean(vals)
            if len(vals) < 2:
                sigma = 0.0
            else:
                sigma = stdev(vals)
            self.param_to_mu_sigma[param] = self.MuSigma(mu=mu, sigma=sigma)

    def _eval_one_param(self, param_name: str, real_value: float) -> float:
        """Вычисляет оценку похожести одного параметра на выборку (чем выше, тем лучше)."""
        mu_sigma = self.param_to_mu_sigma.get(param_name)
        if mu_sigma is None:
            raise ValueError(f"Parameter '{param_name}' not found in training data.")

        mu = mu_sigma.mu
        sigma = mu_sigma.sigma

        # Вычисляем нормированное отклонение
        if sigma == 0:
            # Если все значения в выборке одинаковы, отклонение не имеет смысла — максимальная похожесть
            normalized_deviation = 0.0
        else:
            normalized_deviation = abs(real_value - mu) / sigma

        # Преобразуем отклонение в оценку похожести: чем меньше отклонение, тем выше оценка
        # Используем сигмоидоподобное преобразование для плавного перехода в [0;1]
        score = 1.0 / (1.0 + normalized_deviation)

        return score

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """Возвращает итоговую оценку экземпляра: среднее по оценкам параметров в интервале [0;1]."""
        scores = []
        params_names = exemplar.get_param_names()

        for param_name in params_names:
            real_val = exemplar.get_parameter_value(param_name)
            score = self._eval_one_param(param_name, real_val)
            scores.append(score)

        if not scores:
            return 0.0

        # Нормализуем: среднее по всем параметрам → значение в [0; 1]
        avg_score = sum(scores) / len(scores)
        return avg_score

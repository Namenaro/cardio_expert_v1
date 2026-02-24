from dataclasses import dataclass
from statistics import mean, stdev
from typing import Optional, Dict, List

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.eval import BaseEvaluator


class SumDistsEval(BaseEvaluator):
    """
       Оценивает экземпляр (Exemplar) как сумму нормированных отклонений его параметров
       от матожиданий, вычисленных по позитивной выборке.

       Для каждого параметра отклонение реального значения от матожидания нормируется
       на стандартное отклонение выборки, что обеспечивает сопоставимость вкладов разных параметров.
       """

    @dataclass
    class MuSigma:
        mu: Optional[float] = None
        sigma: Optional[float] = None

    def __init__(self, positive_dataset: ParametrisedDataset):
        self.param_to_mu_sigma: Dict[str, SumDistsEval.MuSigma] = {}
        for param in positive_dataset.param_names:
            vals: List[float] = positive_dataset.get_parameter_values(param)
            mu = mean(vals)
            # Вычисляем стандартное отклонение
            if len(vals) < 2:
                sigma = 0.0  # Если только одно значение, дисперсия нулевая
            else:
                sigma = stdev(vals)  # Стандартное отклонение
            # Сохраняем в словарь
            self.param_to_mu_sigma[param] = self.MuSigma(mu=mu, sigma=sigma)

    def _eval_one_param(self, param_name: str, real_value: float) -> float:
        # Получаем сохранённые mu и sigma для параметра
        mu_sigma = self.param_to_mu_sigma.get(param_name)
        if mu_sigma is None:
            raise ValueError(f"Parameter '{param_name}' not found in training data.")

        mu = mu_sigma.mu
        sigma = mu_sigma.sigma

        # Вычисляем абсолютное отклонение от матожидания
        deviation = abs(real_value - mu)

        # Нормируем на стандартное отклонение
        if sigma == 0:
            # Если sigma = 0, все значения в выборке одинаковы, отклонение не имеет смысла
            normalized_deviation = 0.0
        else:
            normalized_deviation = deviation / sigma

        return normalized_deviation

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        eval_res = 0
        params_names = exemplar.get_param_names()
        for param_name in params_names:
            real_val = exemplar.get_parameter_value(param_name)
            eval_res += self._eval_one_param(param_name, real_val)
        return eval_res

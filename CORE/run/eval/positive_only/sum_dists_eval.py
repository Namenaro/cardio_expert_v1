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

    2. Для каждого параметра оцениваемого экземпляра :
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
    evaluator = SumDistsEval(mock_dataset)

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

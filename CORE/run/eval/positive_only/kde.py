from typing import Dict, List

from scipy.stats import gaussian_kde

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


class KDE_Eval(BaseEvaluator):
    """
    Оценка экземпляра через оценку плотности ядра (Kernel Density Estimation, KDE) с гауссовым ядром.

    Алгоритм:
    1. На этапе инициализации для каждого параметра из позитивной выборки строится непараметрическая оценка плотности распределения (KDE).
    2. Для каждого параметра оцениваемого экземпляра вычисляется плотность вероятности его значения согласно KDE.
    3. Итоговая оценка — среднее значение плотностей по всем параметрам, нормализованное в интервал [0; 1].

    Преимущества:
    * Не требует предположений о форме распределения (непараметрический метод).
    * Устойчив к выбросам.
    * Гибко адаптируется к сложной форме распределения (многомодальность, асимметрия).
    * Естественная интерпретация: высокая плотность — типичное значение, низкая — нетипичное.
    """

    def __init__(self, positive_dataset: ParametrisedDataset):
        """
        Инициализирует объект, строя KDE для каждого параметра позитивной выборки.

        Args:
            positive_dataset (ParametrisedDataset): позитивная выборка для построения KDE.
        """
        self.param_to_kde: Dict[str, gaussian_kde] = {}
        for param in positive_dataset.param_names:
            vals: List[float] = positive_dataset.get_parameter_values(param)
            if len(vals) < 2:
                # Для одиночных значений используем дельта-подобную функцию
                self.param_to_kde[param] = self._create_single_value_kde(vals[0])
            else:
                # Строим KDE с автоматической оценкой ширины окна
                data = np.array(vals)
                self.param_to_kde[param] = gaussian_kde(data)

    def _create_single_value_kde(self, value: float) -> callable:
        """Создаёт KDE‑аналог для одиночного значения."""

        def kde_func(x):
            if np.isscalar(x):
                return 1.0 if np.isclose(x, value) else 0.0
            else:
                return np.array([1.0 if np.isclose(xi, value) else 0.0 for xi in x])

        return kde_func

    def _eval_one_param(self, param_name: str, real_value: float) -> float:
        """
        Вычисляет плотность вероятности значения параметра согласно KDE.

        Args:
            param_name (str): имя параметра.
            real_value (float): значение параметра в экземпляре.

        Returns:
            float: плотность вероятности в точке real_value, нормализованная в [0; 1].
        """
        kde = self.param_to_kde[param_name]
        try:
            # Вычисляем плотность в точке
            density = kde.evaluate([real_value])[0]
            # Нормализуем плотность: ищем максимум на типичном диапазоне значений
            sample_vals = kde.dataset
            sample_densities = kde.evaluate(sample_vals)
            max_density = np.max(sample_densities)
            normalized_score = min(1.0, density / max_density)  # Ограничиваем сверху 1.0
        except Exception:
            normalized_score = 0.0  # В случае ошибки считаем значение нетипичным
        return normalized_score

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Возвращает итоговую оценку экземпляра как среднее по плотностям всех его параметров.

        Args:
            exemplar (Exemplar): экземпляр для оценки.

        Returns:
            float: средняя нормализованная плотность в интервале [0; 1].
        """
        scores = []
        params_names = exemplar.get_param_names()
        for param_name in params_names:
            real_val = exemplar.get_parameter_value(param_name)
            score = self._eval_one_param(param_name, real_val)
            scores.append(score)
        if not scores:
            return 0.0
        # Среднее по всем параметрам
        avg_score = float(np.mean(scores))
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

    test_data = {'param1': param1.tolist(), 'param2': param2.tolist(), 'param3': param3.tolist()}


    def mock_get_parameter_values(param_name):
        return test_data[param_name]


    mock_dataset.get_parameter_values.side_effect = mock_get_parameter_values

    # Создаём mock для Exemplar
    mock_exemplar = Mock()

    # Инициализируем оценщик
    evaluator = KDE_Eval(mock_dataset)

    # Тест 1: Нормальный экземпляр (в центре распределения)
    normal_values = {'param1': 3.0,  # среднее
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
    mild_values = {'param1': 4.0, 'param2': 7.5, 'param3': 2.2}


    def mock_mild_get_value(param_name):
        return mild_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_mild_get_value

    mild_score = evaluator.eval_exemplar(mock_exemplar)
    print(f"Оценка слегка отклоняющегося: {mild_score:.4f}")

    # Тест 3: Выброс
    outlier_values = {'param1': 10.0, 'param2': -5.0, 'param3': 5.0}


    def mock_outlier_get_value(param_name):
        return outlier_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_outlier_get_value

    outlier_score = evaluator.eval_exemplar(mock_exemplar)
    print(f"Оценка выброса: {outlier_score:.4f}")

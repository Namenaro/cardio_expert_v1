import numpy as np
from typing import Dict, List

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.eval import BaseEvaluator


class MahalanobisEval(BaseEvaluator):
    """
    Оценка экземпляра через расстояние Махаланобиса, учитывающее корреляции между параметрами.

    Алгоритм:
    1. На этапе инициализации:
       - собираются все параметры позитивной выборки в матрицу данных;
       - вычисляются вектор средних значений (mean_vector) и ковариационная матрица (cov_matrix);
       - находится обратная ковариационная матрица (inv_cov) для расчёта расстояния.
    2. Для оцениваемого экземпляра:
       - формируется вектор его значений по всем параметрам;
       - вычисляется расстояние Махаланобиса между этим вектором и средним вектором выборки;
       - расстояние преобразуется в оценку похожести.

    Преимущества:
    * учитывает корреляции между параметрами (в отличие от поэлементных методов);
    * инвариантен к масштабу измерений — автоматически нормирует параметры;
    * чувствителен к форме распределения данных в выборке;
    * даёт единую интегральную оценку похожести экземпляра на выборку.

    Интерпретация:
    * 0.0 — экземпляр сильно отличается от позитивной выборки;
    * > 0.7 — экземпляр очень похож на выборку;
    * промежуточные значения — умеренная похожесть.
    """

    def __init__(self, positive_dataset: ParametrisedDataset):
        """
        Инициализирует объект, вычисляя статистику позитивной выборки.

        Args:
            positive_dataset (ParametrisedDataset): позитивная выборка для построения модели.
        """
        # Собираем данные по всем параметрам в матрицу (параметры × наблюдения)
        data_list = []
        self.param_names = positive_dataset.param_names
        for param in self.param_names:
            vals = positive_dataset.get_parameter_values(param)
            data_list.append(vals)

        self.data_matrix = np.array(data_list)  # Форма: (n_params, n_observations)
        self.n_params = len(self.param_names)

        # Вычисляем вектор средних и ковариационную матрицу
        self.mean_vector = np.mean(self.data_matrix, axis=1)  # Вектор средних по каждому параметру
        self.cov_matrix = np.cov(self.data_matrix)  # Ковариационная матрица

        # Обрабатываем случай вырожденной матрицы
        try:
            self.inv_cov = np.linalg.inv(self.cov_matrix)
        except np.linalg.LinAlgError:
            # Если матрица вырождена, добавляем регуляризацию
            epsilon = 1e-8
            self.inv_cov = np.linalg.inv(self.cov_matrix + epsilon * np.eye(self.n_params))

    def _mahalanobis_distance(self, x: np.ndarray) -> float:
        """
        Вычисляет расстояние Махаланобиса между вектором x и средним вектором выборки.

        Args:
            x (np.ndarray): вектор значений экземпляра (форма: (n_params,)).

        Returns:
            float: квадрат расстояния Махаланобиса.
        """
        diff = x - self.mean_vector
        distance_squared = diff.T @ self.inv_cov @ diff
        return distance_squared

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        # Формируем вектор значений экземпляра
        x = np.array([exemplar.get_parameter_value(p) for p in self.param_names])

        # Вычисляем расстояние Махаланобиса
        mahal_dist_sq = self._mahalanobis_distance(x)

        # Преобразуем расстояние в оценку [0;1]
        # Используем нелинейное преобразование для плавного убывания
        score = 1.0 / (1.0 + np.sqrt(mahal_dist_sq))
        return float(score)


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
    evaluator = MahalanobisEval(mock_dataset)

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

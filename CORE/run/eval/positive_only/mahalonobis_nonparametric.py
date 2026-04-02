import numpy as np
from scipy.stats import percentileofscore
from sklearn.preprocessing import StandardScaler

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


class MahalanobisNonparametricEval(BaseEvaluator):
    """
    Оценка экземпляра через непараметрическую интерпретацию расстояний Махаланобиса.
    """

    def __init__(self, positive_dataset: ParametrisedDataset, regularization=1e-6):
        self.positive_dataset = positive_dataset
        self.all_param_names = positive_dataset.param_names
        self.regularization = regularization

        # Собираем данные по всем параметрам
        data_list = [positive_dataset.get_parameter_values(p) for p in self.all_param_names]
        self.full_data_matrix = np.array(data_list)  # shape: (n_features, n_samples)

        # Нормализация данных для устойчивости
        self.scaler = StandardScaler()
        self.full_data_matrix_normalized = self.scaler.fit_transform(self.full_data_matrix.T).T

    def _get_stats_for_params(self, param_names: list) -> tuple:
        """
        Вычисляет статистики (mean_vector, inv_cov, scaler, reference_distances) для указанных параметров.

        Args:
            param_names (list): список имен параметров

        Returns:
            tuple: (scaler, mean_vector, inv_cov, reference_distances)
        """
        # Собираем данные только для указанных параметров
        data_list = []
        for param in param_names:
            vals = self.positive_dataset.get_parameter_values(param)
            data_list.append(vals)

        data_matrix = np.array(data_list)  # shape: (n_features, n_samples)

        # Нормализация данных
        scaler = StandardScaler()
        data_matrix_normalized = scaler.fit_transform(data_matrix.T).T

        mean_vector = np.mean(data_matrix_normalized, axis=1)
        cov_matrix = np.cov(data_matrix_normalized)

        # Регуляризация ковариационной матрицы
        n_features = len(param_names)
        cov_matrix_reg = cov_matrix + self.regularization * np.eye(n_features)

        # Вычисляем обратную матрицу
        try:
            inv_cov = np.linalg.inv(cov_matrix_reg)
        except np.linalg.LinAlgError:
            # Если всё ещё вырождена, используем псевдообратную
            inv_cov = np.linalg.pinv(cov_matrix_reg)

        # Вычисляем эталонное распределение расстояний
        reference_distances = self._compute_reference_distances(data_matrix_normalized, mean_vector, inv_cov)

        return scaler, mean_vector, inv_cov, reference_distances

    def _compute_reference_distances(self, data_matrix_normalized: np.ndarray, mean_vector: np.ndarray,
                                     inv_cov: np.ndarray) -> np.ndarray:
        """Вычисляет расстояния Махаланобиса для всех наблюдений."""
        distances = []
        n_samples = data_matrix_normalized.shape[1]

        for i in range(n_samples):
            x_i = data_matrix_normalized[:, i]
            diff = x_i - mean_vector
            dist_sq = diff.T @ inv_cov @ diff
            distances.append(np.sqrt(max(dist_sq, 0)))

        return np.array(distances)

    def _mahalanobis_distance(self, x: np.ndarray, mean_vector: np.ndarray, inv_cov: np.ndarray) -> float:
        """Вычисляет расстояние Махаланобиса для нормализованного вектора x."""
        diff = x - mean_vector
        dist_sq = diff.T @ inv_cov @ diff
        return np.sqrt(max(dist_sq, 0))

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Возвращает оценку экземпляра в интервале [0; 1].
        """
        # Получаем вектор, матрицу и список общих параметров
        x, data_matrix, common_params = self._get_common_data(
            exemplar, self.all_param_names, self.positive_dataset
        )

        # Если нет общих параметров, возвращаем минимальную оценку
        if x is None:
            return 0.0

        # Получаем статистики для общих параметров
        scaler, mean_vector, inv_cov, reference_distances = self._get_stats_for_params(common_params)

        # Нормализуем вектор
        x_normalized = scaler.transform(x).flatten()

        # Расстояние Махаланобиса
        new_distance = self._mahalanobis_distance(x_normalized, mean_vector, inv_cov)

        # Процентиль в эталонном распределении
        percentile = percentileofscore(reference_distances, new_distance)

        # Инвертируем процентиль в оценку
        score = 1.0 - percentile / 100.0
        return score


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
    evaluator = MahalanobisNonparametricEval(mock_dataset, regularization=1e-4)

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

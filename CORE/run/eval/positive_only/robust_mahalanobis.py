import numpy as np
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import StandardScaler
from scipy.stats import chi2

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


class EllipticEnvelopeEvaluator(BaseEvaluator):
    """
    Оценка экземпляра через Elliptic Envelope (Robust Mahalanobis distance).

    Использует Minimum Covariance Determinant (MCD) для робастной оценки
    ковариационной матрицы, устойчивой к выбросам в эталонной выборке.

    Преимущества:
    - Учитывает корреляции между признаками
    - Устойчив к выбросам в эталоне (в отличие от обычного Махаланобиса)
    - Имеет четкую статистическую интерпретацию
    """

    def __init__(
            self,
            positive_dataset: ParametrisedDataset,
            contamination: float = 0.1,  # ожидаемая доля выбросов в эталоне
            support_fraction: float = 0.7,  # доля точек для MCD
            normalize: bool = True,
            random_state: int = None
    ):
        self.positive_dataset = positive_dataset
        self.all_param_names = positive_dataset.param_names
        self.contamination = contamination
        self.support_fraction = support_fraction
        self.normalize = normalize
        self.random_state = random_state

    def _get_model_for_params(self, param_names: list) -> tuple:
        """
        Обучает Elliptic Envelope для указанных параметров.

        Args:
            param_names (list): список имен параметров

        Returns:
            tuple: (scaler, ee, reference_distances)
        """
        # Собираем данные только для указанных параметров
        data_list = []
        for param in param_names:
            vals = self.positive_dataset.get_parameter_values(param)
            data_list.append(vals)

        data_matrix = np.array(data_list).T

        # Нормализация
        if self.normalize:
            scaler = StandardScaler()
            data_normalized = scaler.fit_transform(data_matrix)
        else:
            scaler = None
            data_normalized = data_matrix

        # Обучаем Elliptic Envelope
        ee = EllipticEnvelope(
            contamination=self.contamination,
            support_fraction=self.support_fraction,
            random_state=self.random_state
        )
        ee.fit(data_normalized)

        # Вычисляем расстояния Махаланобиса для эталона
        reference_distances = ee.mahalanobis(data_normalized)

        return scaler, ee, reference_distances

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Возвращает оценку экземпляра в [0; 1].

        Используем хи-квадрат распределение для преобразования расстояния
        Махаланобиса в вероятность.
        """
        # Получаем вектор, матрицу и список общих параметров
        x, data_matrix, common_params = self._get_common_data(
            exemplar, self.all_param_names, self.positive_dataset
        )

        # Если нет общих параметров, возвращаем минимальную оценку
        if x is None:
            return 0.0

        # Обучаем модель для общих параметров
        scaler, ee, reference_distances = self._get_model_for_params(common_params)

        # Нормализуем вектор
        if scaler is not None:
            x_normalized = scaler.transform(x)
        else:
            x_normalized = x

        # Вычисляем расстояние Махаланобиса
        mahal_dist = ee.mahalanobis(x_normalized)[0]

        # Преобразуем расстояние в вероятность через хи-квадрат
        # Степени свободы = количество признаков
        df = len(common_params)
        p_value = 1 - chi2.cdf(mahal_dist, df)

        # p_value - это вероятность получить такое же или большее расстояние
        # для точки из того же распределения
        # Нормализуем в [0; 1], где 1 = идеальное совпадение
        score = p_value

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
    evaluator = EllipticEnvelopeEvaluator(mock_dataset)

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

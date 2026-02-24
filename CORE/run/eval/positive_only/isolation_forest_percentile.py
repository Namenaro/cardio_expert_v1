import numpy as np
from scipy.stats import percentileofscore
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from CORE.run import Exemplar
from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run.eval.base_eval import BaseEvaluator


class IsolationForestPercentileEvaluator(BaseEvaluator):
    """
     Isolation Forest изолирует аномалии случайными разбиениями пространства.
    Чем меньше разбиений нужно для изоляции точки, тем она более аномальна.

    Оценка = процентиль в эталонном распределении
    """

    def __init__(
            self,
            positive_dataset: ParametrisedDataset,
            n_estimators: int = 100,
            contamination: float = 0.1,
            normalize: bool = True,
            random_state: int = 42
    ):
        self.param_names = positive_dataset.param_names

        # Собираем данные
        data_list = [positive_dataset.get_parameter_values(p) for p in self.param_names]
        self.data_matrix = np.array(data_list).T

        # Нормализация
        if normalize:
            self.scaler = StandardScaler()
            self.data_normalized = self.scaler.fit_transform(self.data_matrix)
        else:
            self.scaler = None
            self.data_normalized = self.data_matrix

        # Обучаем Isolation Forest
        self.iforest = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            bootstrap=True
        )
        self.iforest.fit(self.data_normalized)

        # Вычисляем эталонные оценки
        self.reference_scores = self.iforest.score_samples(self.data_normalized)

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """Оценка = процентиль в эталонном распределении."""
        # Получаем вектор значений
        x_raw = np.array([[
            exemplar.get_parameter_value(p) for p in self.param_names
        ]])

        # Нормализуем
        if self.scaler is not None:
            x = self.scaler.transform(x_raw)
        else:
            x = x_raw

        # Получаем оценку
        iforest_score = self.iforest.score_samples(x)[0]

        # Вычисляем процентиль (доля эталонных точек с меньшей оценкой)
        # Чем выше оценка, тем лучше
        percentile = percentileofscore(self.reference_scores, iforest_score, kind='mean')

        # Нормализуем в [0; 1]
        score = percentile / 100.0

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
    evaluator = IsolationForestPercentileEvaluator(mock_dataset)

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

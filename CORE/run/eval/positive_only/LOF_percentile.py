from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


# Альтернативная версия с другой нормализацией (на основе перцентилей)
class LOFPercentileEvaluator(BaseEvaluator):
    """
    Версия LOF-оценщика с нормализацией через перцентили эталонной выборки.

    Более простая интерпретация: оценка = процентиль LOF-оценки экземпляра
    среди эталонных LOF-оценок.
    """

    def __init__(
            self,
            positive_dataset: ParametrisedDataset,
            n_neighbors: int = 10,
            contamination: float = 'auto',
            normalize: bool = True
    ):
        self.param_names = positive_dataset.param_names
        self.n_neighbors = n_neighbors
        self.contamination = contamination
        self.normalize = normalize

        # Собираем данные
        data_list = [positive_dataset.get_parameter_values(p) for p in self.param_names]
        self.data_matrix = np.array(data_list).T

        # Нормализация
        if self.normalize:
            self.scaler = StandardScaler()
            self.data_normalized = self.scaler.fit_transform(self.data_matrix)
        else:
            self.scaler = None
            self.data_normalized = self.data_matrix

        # Обучаем LOF
        self.lof = LocalOutlierFactor(
            n_neighbors=self.n_neighbors,
            contamination=self.contamination,
            novelty=True
        )
        self.lof.fit(self.data_normalized)

        # Вычисляем эталонные LOF-оценки
        self.reference_scores = self.lof.negative_outlier_factor_

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Оценка = доля эталонных точек с LOF-оценкой МЕНЬШЕ, чем у экземпляра.

        Так как LOF-оценки отрицательные и чем меньше (более отрицательная),
        тем точка более аномальна, то:
        - Нормальная точка получает оценку близкую к 1 (высокий процентиль)
        - Выброс получает оценку близкую к 0 (низкий процентиль)
        """
        from scipy.stats import percentileofscore

        # Получаем вектор значений
        x_raw = np.array([[
            exemplar.get_parameter_value(p) for p in self.param_names
        ]])

        # Нормализуем
        if self.normalize and self.scaler is not None:
            x = self.scaler.transform(x_raw)
        else:
            x = x_raw

        # Получаем LOF-оценку
        try:
            lof_score = self.lof.score_samples(x)[0]
        except AttributeError:
            lof_score = self.lof.decision_function(x)[0]

        # Вычисляем процентиль
        # Важно: так как LOF-оценки отрицательные, используем kind='weak'
        percentile = percentileofscore(self.reference_scores, lof_score, kind='weak')

        # Нормализуем в [0; 1]
        score = percentile / 100.0

        return score


if __name__ == "__main__":
    from unittest.mock import Mock
    import numpy as np

    # Создаём тестовые данные
    np.random.seed(42)
    n_samples = 100

    # Генерируем два кластера нормальных точек
    # Кластер 1
    param1 = np.concatenate([
        np.random.normal(3, 0.5, n_samples // 2),
        np.random.normal(7, 0.5, n_samples // 2)
    ])
    param2 = np.concatenate([
        np.random.normal(5, 0.5, n_samples // 2),
        np.random.normal(10, 0.5, n_samples // 2)
    ])
    param3 = np.concatenate([
        np.random.normal(1, 0.2, n_samples // 2),
        np.random.normal(2, 0.2, n_samples // 2)
    ])

    # Добавляем немного шума
    param1 += np.random.normal(0, 0.1, n_samples)
    param2 += np.random.normal(0, 0.1, n_samples)
    param3 += np.random.normal(0, 0.05, n_samples)

    test_data = {
        'param1': param1.tolist(),
        'param2': param2.tolist(),
        'param3': param3.tolist()
    }

    # Создаём mock для ParametrisedDataset
    mock_dataset = Mock()
    mock_dataset.param_names = ['param1', 'param2', 'param3']


    def mock_get_parameter_values(param_name):
        return test_data[param_name]


    mock_dataset.get_parameter_values.side_effect = mock_get_parameter_values

    # Создаём mock для Exemplar
    mock_exemplar = Mock()
    mock_exemplar.get_param_names.return_value = ['param1', 'param2', 'param3']

    # Инициализируем оценщик
    evaluator = LOFPercentileEvaluator(
        mock_dataset,
        n_neighbors=20,
        normalize=True
    )

    # Тест 1: Точка из первого кластера
    cluster1_values = {'param1': 3.0, 'param2': 5.0, 'param3': 1.0}


    def mock_cluster1_value(param_name):
        return cluster1_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_cluster1_value

    score1 = evaluator.eval_exemplar(mock_exemplar)
    print(f"\nОценка точки из кластера 1: {score1:.4f}")

    # Тест 2: Точка из второго кластера
    cluster2_values = {'param1': 7.0, 'param2': 10.0, 'param3': 2.0}


    def mock_cluster2_value(param_name):
        return cluster2_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_cluster2_value

    score2 = evaluator.eval_exemplar(mock_exemplar)
    print(f"\nОценка точки из кластера 2: {score2:.4f}")

    # Тест 3: Точка на границе
    boundary_values = {'param1': 5.0, 'param2': 7.5, 'param3': 1.5}


    def mock_boundary_value(param_name):
        return boundary_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_boundary_value

    score3 = evaluator.eval_exemplar(mock_exemplar)
    print(f"\nОценка точки на границе: {score3:.4f}")

    # Тест 4: Явный выброс
    outlier_values = {'param1': 20.0, 'param2': 30.0, 'param3': 10.0}


    def mock_outlier_value(param_name):
        return outlier_values[param_name]


    mock_exemplar.get_parameter_value.side_effect = mock_outlier_value

    score4 = evaluator.eval_exemplar(mock_exemplar)
    print(f"\nОценка выброса: {score4:.4f}")

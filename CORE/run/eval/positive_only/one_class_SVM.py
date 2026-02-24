from sklearn.preprocessing import RobustScaler  # более устойчив к выбросам
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


class OneClassSVMEvaluator(BaseEvaluator):
    """
    Оценка экземпляра через One-Class SVM.

    One-Class SVM строит границу, отделяющую эталонные точки от остального пространства.
    Оценка = сигмоида от расстояния до границы решения.

    Преимущества:
    - Работает в высокоразмерных пространствах
    - Может находить нелинейные границы (с RBF ядром)
    - Устойчив к выбросам (параметр nu)
    """

    def __init__(
            self,
            positive_dataset: ParametrisedDataset,
            kernel: str = 'rbf',
            nu: float = 0.1,  # ожидаемая доля выбросов в эталоне
            gamma: str = 'scale',  # параметр RBF ядра
            normalize: bool = True,
            use_robust_scaler: bool = True
    ):
        self.param_names = positive_dataset.param_names
        self.nu = nu
        self.gamma = gamma
        self.normalize = normalize

        # Собираем данные
        data_list = [positive_dataset.get_parameter_values(p) for p in self.param_names]
        self.data_matrix = np.array(data_list).T

        # Нормализация (RobustScaler лучше для данных с выбросами)
        if self.normalize:
            if use_robust_scaler:
                self.scaler = RobustScaler()
            else:
                self.scaler = StandardScaler()
            self.data_normalized = self.scaler.fit_transform(self.data_matrix)
        else:
            self.scaler = None
            self.data_normalized = self.data_matrix

        # Обучаем One-Class SVM
        self.svm = OneClassSVM(kernel=kernel, nu=nu, gamma=gamma)
        self.svm.fit(self.data_normalized)

        # Вычисляем эталонные оценки для калибровки
        self.reference_scores = self.svm.score_samples(self.data_normalized)

    def _sigmoid_normalize(self, score: float) -> float:
        """Нормализует оценку SVM в интервал [0; 1] через сигмоиду."""
        # Масштабируем относительно медианы эталонных оценок
        median_score = np.median(self.reference_scores)
        scaled = (score - median_score) / (self.reference_scores.std() + 1e-8)

        # Сигмоида: 1 / (1 + exp(-scaled))
        normalized = 1.0 / (1.0 + np.exp(-scaled))
        return float(normalized)

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """Возвращает оценку экземпляра в [0; 1]."""
        # Получаем вектор значений
        x_raw = np.array([[
            exemplar.get_parameter_value(p) for p in self.param_names
        ]])

        # Нормализуем
        if self.scaler is not None:
            x = self.scaler.transform(x_raw)
        else:
            x = x_raw

        # Получаем оценку от SVM
        svm_score = self.svm.score_samples(x)[0]

        # Нормализуем в [0; 1]
        score = self._sigmoid_normalize(svm_score)

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
    evaluator = OneClassSVMEvaluator(mock_dataset)

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

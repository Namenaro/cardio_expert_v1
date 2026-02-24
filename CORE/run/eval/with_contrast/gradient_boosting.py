from sklearn.ensemble import GradientBoostingClassifier

from CORE.run import Exemplar
from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run.eval.base_eval import BaseEvaluator


class GradientBoostingEvaluator(BaseEvaluator):
    """
    Оценка экземпляра через Gradient Boosting.

    Gradient Boosting последовательно строит деревья, каждое следующее
    исправляет ошибки предыдущих.

    Преимущества:
    - Устойчив к выбросам (при использовании robust loss)
    - Не требует нормализации

    """

    def __init__(
            self,
            positive_dataset: ParametrisedDataset,
            contrast_dataset: ParametrisedDataset,
            n_estimators: int = 100,
            max_depth: int = 3,  # небольшая глубина для регуляризации
            learning_rate: float = 0.1,
            subsample: float = 0.8,  # использовать 80% данных для каждого дерева
            random_state: int = 42
    ):
        # Проверяем совместимость параметров
        if positive_dataset.param_names != contrast_dataset.param_names:
            raise ValueError("Позитивная и контрастная выборки должны иметь одинаковые параметры")

        self.param_names = positive_dataset.param_names

        # Собираем данные
        pos_data_list = [positive_dataset.get_parameter_values(p) for p in self.param_names]
        contrast_data_list = [contrast_dataset.get_parameter_values(p) for p in self.param_names]

        self.pos_data = np.array(pos_data_list).T
        self.contrast_data = np.array(contrast_data_list).T

        # Объединяем
        X = np.vstack([self.pos_data, self.contrast_data])
        y = np.hstack([np.ones(len(self.pos_data)), np.zeros(len(self.contrast_data))])

        # Обучаем Gradient Boosting
        self.gb = GradientBoostingClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            random_state=random_state
        )
        self.gb.fit(X, y)

        # Важность признаков
        self.feature_importances = dict(zip(self.param_names, self.gb.feature_importances_))

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Возвращает вероятность принадлежности к позитивному классу.
        """
        # Получаем вектор значений
        x = np.array([[
            exemplar.get_parameter_value(p) for p in self.param_names
        ]])

        # Получаем вероятности
        proba = self.gb.predict_proba(x)[0]

        # Находим индекс позитивного класса
        pos_class_idx = np.where(self.gb.classes_ == 1)[0][0]
        score = proba[pos_class_idx]

        return float(score)


if __name__ == "__main__":
    from unittest.mock import Mock
    import numpy as np

    # Создаём синтетические данные
    np.random.seed(42)
    n_samples = 100

    # Позитивный класс - два кластера (нелинейная разделимость)
    pos_cluster1 = np.random.multivariate_normal([2, 2], [[0.3, 0.1], [0.1, 0.3]], n_samples // 2)
    pos_cluster2 = np.random.multivariate_normal([6, 6], [[0.3, -0.1], [-0.1, 0.3]], n_samples // 2)
    pos_data = np.vstack([pos_cluster1, pos_cluster2])

    # Контрастный класс - между кластерами и вокруг
    contrast_data = np.random.uniform(low=0, high=8, size=(n_samples, 2))

    # Создаём mock для датасетов
    mock_pos_dataset = Mock()
    mock_pos_dataset.param_names = ['param1', 'param2']
    mock_contrast_dataset = Mock()
    mock_contrast_dataset.param_names = ['param1', 'param2']


    def mock_pos_get_values(param_name):
        return pos_data[:, 0].tolist() if param_name == 'param1' else pos_data[:, 1].tolist()


    def mock_contrast_get_values(param_name):
        return contrast_data[:, 0].tolist() if param_name == 'param1' else contrast_data[:, 1].tolist()


    mock_pos_dataset.get_parameter_values.side_effect = mock_pos_get_values
    mock_contrast_dataset.get_parameter_values.side_effect = mock_contrast_get_values

    # Создаём mock для Exemplar
    mock_exemplar = Mock()
    mock_exemplar.get_param_names.return_value = ['param1', 'param2']

    # Инициализируем оценщик
    evaluator = GradientBoostingEvaluator(
        mock_pos_dataset,
        mock_contrast_dataset
    )

    # Тестируем разные точки
    test_points = [
        ("Центр позитивного кластера 1", [2.0, 2.0]),
        ("Центр позитивного кластера 2", [6.0, 6.0]),
        ("Граница между кластерами", [4.0, 4.0]),
        ("Область контрастного класса", [1.0, 6.0]),
        ("Сильный выброс", [10.0, 10.0])
    ]

    for name, point in test_points:
        def mock_get_value(param_name):
            return point[0] if param_name == 'param1' else point[1]


        mock_exemplar.get_parameter_value.side_effect = mock_get_value

        score = evaluator.eval_exemplar(mock_exemplar)
        print(f"{name} ---->: {score:.4f}")

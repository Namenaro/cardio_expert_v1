from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


class KNNBinaryEvaluator(BaseEvaluator):
    """
    Оценка экземпляра через KNN для двух выборок (позитивная vs контрастная).

    Самый простой нелинейный классификатор.
    KNN автоматически подбирает оптимальное число соседей через кросс-валидацию.

    Для нового экземпляра возвращается доля позитивных соседей среди k ближайших.
    """

    def __init__(
            self,
            positive_dataset: ParametrisedDataset,
            contrast_dataset: ParametrisedDataset,
            max_k: int = 20
    ):
        """
        Параметры:
        ----------
        positive_dataset : ParametrisedDataset
            Позитивная выборка (целевой класс)
        contrast_dataset : ParametrisedDataset
            Контрастная выборка (отрицательный класс)
        max_k : int
            Максимальное число соседей для перебора
        """
        # Проверяем совместимость параметров
        if positive_dataset.param_names != contrast_dataset.param_names:
            raise ValueError("Позитивная и контрастная выборки должны иметь одинаковые параметры")

        self.param_names = positive_dataset.param_names
        self.max_k = max_k

        # Собираем данные из обоих датасетов
        pos_data_list = [positive_dataset.get_parameter_values(p) for p in self.param_names]
        contrast_data_list = [contrast_dataset.get_parameter_values(p) for p in self.param_names]

        # Транспонируем для получения (n_samples, n_features)
        self.pos_data = np.array(pos_data_list).T
        self.contrast_data = np.array(contrast_data_list).T

        # Объединяем данные и создаем метки
        self.X = np.vstack([self.pos_data, self.contrast_data])
        self.y = np.hstack([np.ones(len(self.pos_data)), np.zeros(len(self.contrast_data))])

        # Нормализация (критически важна для KNN!)
        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(self.X)

        # Подбираем оптимальное k
        self.n_neighbors = self._find_optimal_k()

        # Создаем финальный классификатор
        self.knn = KNeighborsClassifier(
            n_neighbors=self.n_neighbors,
            weights='distance'  # ближайшие соседи имеют больший вес
        )
        self.knn.fit(self.X_scaled, self.y)

    def _find_optimal_k(self) -> int:
        """
        Подбирает оптимальное число соседей через кросс-валидацию.
        Возвращает k, максимизирующее accuracy.
        """
        # Возможные значения k (только нечетные для избежания равенства голосов)
        max_k = min(self.max_k, len(self.X) // 3)
        k_range = range(1, max_k + 1, 2)  # только нечетные

        best_k = 3  # значение по умолчанию
        best_score = 0

        for k in k_range:
            knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
            scores = cross_val_score(knn, self.X_scaled, self.y, cv=5, scoring='accuracy')
            mean_score = scores.mean()

            if mean_score > best_score:
                best_score = mean_score
                best_k = k

        return best_k

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Возвращает вероятность принадлежности экземпляра к позитивному классу.
        """
        # Получаем вектор значений
        x_raw = np.array([[
            exemplar.get_parameter_value(p) for p in self.param_names
        ]])

        # Нормализуем
        x = self.scaler.transform(x_raw)

        # Получаем вероятности
        proba = self.knn.predict_proba(x)[0]

        # Находим индекс позитивного класса (метка 1)
        pos_class_idx = np.where(self.knn.classes_ == 1)[0][0]
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
    evaluator = KNNBinaryEvaluator(
        mock_pos_dataset,
        mock_contrast_dataset,
        max_k=20
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

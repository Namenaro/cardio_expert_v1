from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


class RBFSVMEvaluator(BaseEvaluator):
    """
    Оценка экземпляра через SVM с RBF ядром.

    RBF ядро проецирует данные в бесконечномерное пространство признаков,
    позволяя строить сколь угодно сложные нелинейные разделяющие поверхности.

    Преимущества:
    - Очень гибкий, может моделировать сложные границы
    - Меньше подвержен переобучению, чем KNN (благодаря максимизации зазора)
    - Работает хорошо даже с небольшим количеством данных
    """

    def __init__(self, positive_dataset: ParametrisedDataset, contrast_dataset: ParametrisedDataset, C: float = 1.0,
                 # параметр регуляризации (чем меньше, тем устойчивее к выбросам)
            gamma: str = 'scale',  # 'scale', 'auto' или число (влияние одного примера)
            class_weight: str = 'balanced',  # балансировка классов
            probability: bool = True,  # возвращать калиброванные вероятности
                 random_state: int = 42):
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

        # Нормализация (критически важна для SVM!)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Обучаем SVM с RBF ядром
        self.svm = SVC(kernel='rbf', C=C, gamma=gamma, class_weight=class_weight, probability=probability,
                       # для получения калиброванных вероятностей
                       random_state=random_state)
        self.svm.fit(X_scaled, y)

        # Вычисляем accuracy на обучающей выборке
        self.train_accuracy = self.svm.score(X_scaled, y)

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Возвращает вероятность принадлежности к позитивному классу.
        """
        # Получаем вектор значений
        x_raw = np.array([[exemplar.get_parameter_value(p) for p in self.param_names]])

        # Нормализуем
        x = self.scaler.transform(x_raw)

        # Получаем вероятность класса 1
        proba = self.svm.predict_proba(x)[0]

        # Находим индекс позитивного класса
        pos_class_idx = np.where(self.svm.classes_ == 1)[0][0]
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
    evaluator = RBFSVMEvaluator(mock_pos_dataset, mock_contrast_dataset)

    # Тестируем разные точки
    test_points = [("Центр позитивного кластера 1", [2.0, 2.0]), ("Центр позитивного кластера 2", [6.0, 6.0]),
                   ("Граница между кластерами", [4.0, 4.0]), ("Область контрастного класса", [1.0, 6.0]),
                   ("Сильный выброс", [10.0, 10.0])]

    for name, point in test_points:
        def mock_get_value(param_name):
            return point[0] if param_name == 'param1' else point[1]


        mock_exemplar.get_parameter_value.side_effect = mock_get_value

        score = evaluator.eval_exemplar(mock_exemplar)
        print(f"{name} ---->: {score:.4f}")

from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.run import Exemplar
from CORE.run.eval.base_eval import BaseEvaluator


class PyTorchMLPEvaluator(BaseEvaluator):
    """
    Оценка экземпляра через нейронную сеть (MLP) на PyTorch.

    Двухслойный перцептрон для бинарной классификации.

    """

    def __init__(
            self,
            positive_dataset: ParametrisedDataset,
            contrast_dataset: ParametrisedDataset,
            hidden_sizes: Optional[list] = None,  # размеры скрытых слоев
            activation: str = 'relu',  # 'relu', 'tanh', 'sigmoid'
            dropout_rate: float = 0.2,  # dropout для регуляризации
            learning_rate: float = 0.001,
            batch_size: int = 32,
            epochs: int = 100,
            early_stopping_patience: int = 10,
            validation_split: float = 0.2,
            weight_decay: float = 1e-4,  # L2 регуляризация
            device: str = None,  # 'cuda', 'cpu', или None для автоопределения
            random_state: int = 42,
            verbose: bool = True
    ):
        """
        Параметры:
        ----------
        positive_dataset : ParametrisedDataset
            Позитивная выборка (целевой класс)
        contrast_dataset : ParametrisedDataset
            Контрастная выборка (отрицательный класс)
        hidden_sizes : list
            Размеры скрытых слоев
        activation : str
            Функция активации
        dropout_rate : float
            Вероятность dropout
        learning_rate : float
            Скорость обучения
        batch_size : int
            Размер батча
        epochs : int
            Максимальное количество эпох
        early_stopping_patience : int
            Терпение для ранней остановки
        validation_split : float
            Доля данных для валидации
        weight_decay : float
            L2 регуляризация
        device : str
            Устройство для вычислений
        random_state : int
            Для воспроизводимости
        verbose : bool
            Выводить информацию об обучении
        """
        # Проверяем совместимость параметров
        if positive_dataset.param_names != contrast_dataset.param_names:
            raise ValueError("Позитивная и контрастная выборки должны иметь одинаковые параметры")

        self.param_names = positive_dataset.param_names
        self.hidden_sizes = hidden_sizes
        self.activation = activation
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.early_stopping_patience = early_stopping_patience
        self.validation_split = validation_split
        self.weight_decay = weight_decay
        self.random_state = random_state
        self.verbose = verbose

        # Определяем устройство
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        # Устанавливаем seed для воспроизводимости
        torch.manual_seed(random_state)
        np.random.seed(random_state)

        # Собираем данные
        pos_data_list = [positive_dataset.get_parameter_values(p) for p in self.param_names]
        contrast_data_list = [contrast_dataset.get_parameter_values(p) for p in self.param_names]

        self.pos_data = np.array(pos_data_list).T
        self.contrast_data = np.array(contrast_data_list).T

        # Объединяем
        X = np.vstack([self.pos_data, self.contrast_data])
        y = np.hstack([np.ones(len(self.pos_data)), np.zeros(len(self.contrast_data))])

        # Нормализация
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Разделяем на обучающую и валидационную выборки
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y,
            test_size=validation_split,
            random_state=random_state,
            stratify=y  # сохраняем пропорции классов
        )

        # Создаем модель
        self.model = MLPBinaryClassifier(
            input_size=len(self.param_names),
            hidden_sizes=hidden_sizes,
            activation=activation,
            dropout_rate=dropout_rate
        ).to(self.device)

        # Обучаем модель
        self._train_model(X_train, y_train, X_val, y_val)

        # Оценка на обучающей выборке
        self.train_accuracy = self._evaluate_accuracy(X_scaled, y)

        if self.verbose:
            print(f"\nPyTorchMLPEvaluator инициализирован:")
            print(f"  - Устройство: {self.device}")
            print(f"  - Позитивных: {len(self.pos_data)}")
            print(f"  - Контрастных: {len(self.contrast_data)}")
            print(f"  - Признаков: {len(self.param_names)}")
            print(f"  - Архитектура: {hidden_sizes}")
            print(f"  - Активация: {activation}")
            print(f"  - Dropout: {dropout_rate}")
            print(f"  - Параметров: {sum(p.numel() for p in self.model.parameters())}")
            print(f"  - Точность на обучении: {self.train_accuracy:.3f}")

    def _train_model(self, X_train, y_train, X_val, y_val):
        """
        Обучение модели.
        """
        # Создаем даталоадеры
        train_dataset = TensorDataset(
            torch.FloatTensor(X_train),
            torch.FloatTensor(y_train).unsqueeze(1)
        )
        val_dataset = TensorDataset(
            torch.FloatTensor(X_val),
            torch.FloatTensor(y_val).unsqueeze(1)
        )

        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size)

        # Функция потерь и оптимизатор
        criterion = nn.BCEWithLogitsLoss()  # более устойчиво, чем sigmoid + BCELoss
        optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )

        # Снижение learning rate при плато
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', patience=5, factor=0.5
        )

        # Ранняя остановка
        best_val_loss = float('inf')
        patience_counter = 0
        best_model_state = None

        for epoch in range(self.epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0

            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

                # Считаем accuracy
                predicted = (torch.sigmoid(outputs) > 0.5).float()
                train_correct += (predicted == batch_y).sum().item()
                train_total += batch_y.size(0)

            train_loss /= len(train_loader)
            train_acc = train_correct / train_total

            # Validation
            self.model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0

            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)

                    val_loss += loss.item()

                    predicted = (torch.sigmoid(outputs) > 0.5).float()
                    val_correct += (predicted == batch_y).sum().item()
                    val_total += batch_y.size(0)

            val_loss /= len(val_loader)
            val_acc = val_correct / val_total

            # Scheduler step
            scheduler.step(val_loss)

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_model_state = self.model.state_dict().copy()
            else:
                patience_counter += 1

            if patience_counter >= self.early_stopping_patience:
                if self.verbose:
                    print(f"  - Ранняя остановка на эпохе {epoch + 1}")
                break

            if self.verbose and (epoch + 1) % 20 == 0:
                current_lr = optimizer.param_groups[0]['lr']
                print(f"  - Эпоха {epoch + 1}: train_loss={train_loss:.4f}, train_acc={train_acc:.3f}, "
                      f"val_loss={val_loss:.4f}, val_acc={val_acc:.3f}, lr={current_lr:.6f}")

        # Загружаем лучшую модель
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)

    def _evaluate_accuracy(self, X, y):
        """Оценивает точность на данных."""
        self.model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)
        y_tensor = torch.FloatTensor(y).unsqueeze(1).to(self.device)

        with torch.no_grad():
            outputs = self.model(X_tensor)
            predicted = (torch.sigmoid(outputs) > 0.5).float()
            accuracy = (predicted == y_tensor).float().mean().item()

        return accuracy

    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Возвращает вероятность принадлежности к позитивному классу.
        """
        # Получаем вектор значений
        x_raw = np.array([[
            exemplar.get_parameter_value(p) for p in self.param_names
        ]])

        # Нормализуем
        x = self.scaler.transform(x_raw)

        # Преобразуем в тензор и предсказываем
        self.model.eval()
        x_tensor = torch.FloatTensor(x).to(self.device)

        with torch.no_grad():
            logits = self.model(x_tensor)
            probability = torch.sigmoid(logits).cpu().numpy()[0, 0]

        return float(probability)

    def predict_proba_batch(self, X: np.ndarray) -> np.ndarray:
        """
        Предсказывает вероятности для батча данных.
        Полезно для массовой оценки.
        """
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)

        self.model.eval()
        with torch.no_grad():
            logits = self.model(X_tensor)
            probabilities = torch.sigmoid(logits).cpu().numpy()

        return probabilities.flatten()


class MLPBinaryClassifier(nn.Module):
    """
    Двухслойный перцептрон для бинарной классификации.
    """

    def __init__(self, input_size: int, hidden_sizes: list, activation: str = 'relu', dropout_rate: float = 0.2):
        super().__init__()

        # Выбираем функцию активации
        if activation == 'relu':
            act_fn = nn.ReLU()
        elif activation == 'tanh':
            act_fn = nn.Tanh()
        elif activation == 'sigmoid':
            act_fn = nn.Sigmoid()
        else:
            raise ValueError(f"Неизвестная функция активации: {activation}")

        # Строим слои
        layers = []
        prev_size = input_size

        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.BatchNorm1d(hidden_size),  # нормализация для стабильности
                act_fn,
                nn.Dropout(dropout_rate)
            ])
            prev_size = hidden_size

        # Выходной слой (без активации - будет в loss функции)
        layers.append(nn.Linear(prev_size, 1))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)


if __name__ == "__main__":
    from unittest.mock import Mock

    # Создаём синтетические данные
    np.random.seed(42)
    n_samples = 200

    # Позитивный класс - два кластера (нелинейная разделимость)
    pos_cluster1 = np.random.multivariate_normal([2, 2], [[0.3, 0.1], [0.1, 0.3]], n_samples // 2)
    pos_cluster2 = np.random.multivariate_normal([6, 6], [[0.3, -0.1], [-0.1, 0.3]], n_samples // 2)
    pos_data = np.vstack([pos_cluster1, pos_cluster2])

    # Контрастный класс
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

    print("ТЕСТИРОВАНИЕ PyTorch MLP EVALUATOR")
    print("=" * 60)

    # Инициализируем оценщик
    evaluator = PyTorchMLPEvaluator(
        mock_pos_dataset,
        mock_contrast_dataset,
        hidden_sizes=[32, 16],
        epochs=100,
        verbose=True
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
        print(f"\n{'=' * 50}")
        print(f"ТОЧКА: {name} {point}")


        def mock_get_value(param_name):
            return point[0] if param_name == 'param1' else point[1]


        mock_exemplar.get_parameter_value.side_effect = mock_get_value

        score = evaluator.eval_exemplar(mock_exemplar)
        print(f"РЕЗУЛЬТАТ: {score:.4f}")

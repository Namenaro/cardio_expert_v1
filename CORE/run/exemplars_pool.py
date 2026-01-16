from CORE import Signal
from CORE.run import Exemplar
from typing import List, Optional

class ExemplarsPool:
    """Набор конкурирующих между собой экземпляров одной и той же формы на одном и том же сигнале."""

    def __init__(self, signal: Signal, max_size: Optional[int] = None):
        """
        :param signal: сигнал, к которому относятся экземпляры
        :param max_size: максимальное количество экземпляров в пуле (None — без ограничения)
        """
        self.signal = signal
        self.max_size = max_size
        self.exemplars_sorted: List[
            Exemplar] = []  # Список экземпляров, отсортированный по evaluation_result (убывание)

    def add_exemplar(self, exemplar: Exemplar) -> None:
        """
        Добавляет экземпляр в пул и сохраняет сортировку по evaluation_result (по убыванию).
        При превышении max_size удаляет худший экземпляр.

        :param exemplar: экземпляр Exemplar для добавления
        :raises ValueError: если exemplar имеет незаполненное поле с оценкой
        """
        eval_result = exemplar.evaluation_result
        if eval_result is None:
            raise ValueError("Попытка вставить в пул экземпляр без оценки")

        # Находим позицию для вставки (бинарный поиск)
        left, right = 0, len(self.exemplars_sorted)
        while left < right:
            mid = (left + right) // 2
            mid_eval = self.exemplars_sorted[mid].evaluation_result
            if mid_eval > eval_result:
                left = mid + 1
            else:
                right = mid

        self.exemplars_sorted.insert(left, exemplar)

        # Проверяем ограничение max_size
        if self.max_size is not None and len(self.exemplars_sorted) > self.max_size:
            # Удаляем последний элемент (худший по evaluation_result)
            self.exemplars_sorted.pop()

    @property
    def size(self) -> int:
        """Возвращает количество экземпляров в пуле."""
        return len(self.exemplars_sorted)

    def get_top_n_exemplars_sorted(self, n: int) -> List[Exemplar]:
        """
        Возвращает топ‑n экземпляров, отсортированных по evaluation_result (по убыванию).

        :param n: количество экземпляров для возврата (если n > size, возвращаются все)
        :return: список из n лучших экземпляров (или всех, если их меньше n)
        """
        if n <= 0:
            return []
        return self.exemplars_sorted[:n]

    def clear(self) -> None:
        """Очищает пул от всех экземпляров."""
        self.exemplars_sorted.clear()

    def __iter__(self):
        """Позволяет итерироваться по экземплярам в порядке убывания evaluation_result."""
        return iter(self.exemplars_sorted)

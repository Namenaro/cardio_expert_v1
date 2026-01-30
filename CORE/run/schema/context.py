from typing import List


class Context:
    """
    Хранить то, что уже сделано к текущему шагу распознавания формы, т.е.
    какие посчитаны параметры, какие точки поставлены, какие условия проверены
    """

    def __init__(self):
        self.points_done: List[str] = []
        self.params_done: List[str] = []

        self.HCs_ids_done: List[int] = []
        self.PCs_ids_done: List[int] = []

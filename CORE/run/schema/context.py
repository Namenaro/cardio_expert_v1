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

        self.errors: List[str] = []
        self.nums_of_steps_done: List[int] = []

    def add_point(self, name: str) -> bool:
        """
        Добавляет точку в список выполненных.
        :return: True, если точка ранее не была добавлена; False, если уже присутствовала.
        """
        was_present = name in self.points_done
        self.points_done.append(name)

        if was_present:
            step = self.nums_of_steps_done[-1] if self.nums_of_steps_done else -1
            self.errors.append(f"Попытка повторно добавить точку '{name}' после шага {step}")
            return False
        return True

    def add_param(self, name: str) -> bool:
        """
        Добавляет параметр в список выполненных.
        :return: True, если параметр ранее не был добавлен; False, если уже присутствовал.
        """
        was_present = name in self.params_done
        self.params_done.append(name)

        if was_present:
            step = self.nums_of_steps_done[-1] if self.nums_of_steps_done else -1
            self.errors.append(f"Попытка повторно добавить параметр '{name}' после шага {step}")
            return False
        return True

    def add_PC(self, pazzle_id: int) -> bool:
        """
        Добавляет ID PC в список выполненных.
        :return: True, если ID ранее не был добавлен; False, если уже присутствовал.
        """
        was_present = pazzle_id in self.PCs_ids_done
        self.PCs_ids_done.append(pazzle_id)

        if was_present:
            step = self.nums_of_steps_done[-1] if self.nums_of_steps_done else -1
            self.errors.append(f"Попытка повторно добавить PC с ID {pazzle_id} после шага {step}")
            return False
        return True

    def add_HC(self, pazzle_id: int) -> bool:
        """
        Добавляет ID HC в список выполненных.
        :return: True, если ID ранее не был добавлен; False, если уже присутствовал.
        """
        was_present = pazzle_id in self.HCs_ids_done
        self.HCs_ids_done.append(pazzle_id)

        if was_present:
            step = self.nums_of_steps_done[-1] if self.nums_of_steps_done else -1
            self.errors.append(f"Попытка повторно добавить HC с ID {pazzle_id} после шага {step}")
            return False
        return True

    def add_error(self, err_message: str) -> None:
        self.errors.append(err_message)

    def is_ok(self) -> bool:
        return len(self.errors) == 0

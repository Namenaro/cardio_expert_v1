from abc import ABC, abstractmethod

from CORE.run import Exemplar


class BaseEvaluator(ABC):
    """ Базовый класс для оценщиков"""

    @abstractmethod
    def eval_exemplar(self, exemplar: Exemplar) -> float:
        """
        Посчитать оценку того, насколько "вероятно", что данный экземпляр действительно является экземпляром данной формы.
        :param exemplar: оцениваемый экземпляр формы. Возможно, заполненный лишь частично.
        :return: оценка из интервала [0;1], интерпретируемая как правдоподобие, уверенность (выше - лучше).
        """
        pass

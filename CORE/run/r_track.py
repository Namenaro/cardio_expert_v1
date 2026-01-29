from copy import deepcopy
from itertools import chain
from typing import List

from CORE import Signal
from CORE.db_dataclasses import Track
from CORE.exeptions import RunTrackError, RunPazzleError, PazzleOutOfSignal
from CORE.run.r_ps import R_PS
from CORE.run.r_sm import R_SM
from CORE.run.utils import delete_similar_points


class RTrack:
    """Класс для запуска трека на сигнале в заданном месте"""
    def __init__(self, track: Track):
        self.id: int = track.id

        self.rSM_objects: List[R_SM] = [R_SM(base_pazzle=sm) for sm in track.SMs]
        self.rPS_objects: List[R_PS] = [R_PS(base_pazzle=rs) for rs in track.PSs]

    def run(self, signal: Signal, left_t: float, right_t: float) -> List[float]:
        """
        Основная функция по применению трека к сигналу. Сначала последовательно
        применяет к сигнулу объекты SM, и затем к итоговому модидифицированному
        ими сигналу применяет (независимые друг от друга) объекты PS.
         Возвращает список координат найденных этими объектами особых точек, расположенных
        внутри интервала [left_t, right_t] и не содержащий дублей.

        Входной сигнал не изменяется, работа только с deepcopy.

        :param signal: длинный сигнал, на основе которого конструкируется можификация
        :param left_t: левая граница интервала
        :param right_t: правая граница интервала
        :raises RunTrackError, PazzleOutOfSignal
        :return:
        """
        if len(signal):
            raise RunTrackError.emty_signal(self.id)

        try:

            # 1. Запускаем SM-объекты в том  порядке, в каком они идут в списке и получаем измененный сигнал
            new_signal = self._modify_signal(signal, left_t=left_t, right_t=right_t)

            # 2. Запускаем PS-объекты на измененном сигнале
            points_selected = list(
                chain.from_iterable(obj.run(new_signal, left_t, right_t) for obj in self.rPS_objects)
            )
        except RunPazzleError as e:
            raise RunTrackError.internal_problem_in_pazzle(track_id=self.id, error=str(e))
        except PazzleOutOfSignal:
            # не имеет смысла выполнять этот трек, т..к. один из его SM вылез за пределы доступного сигнала.
            # Но это не обязательно аварийная ситуация - поэтому надо переделать наверх, шагу
            raise

        if any(point < left_t or point > right_t for point in points_selected):
            raise RunTrackError.selected_points_out_of_interval(track_id=self.id, right_t=right_t, left_t=left_t)

        # 3. Прореживаем дубли среди итоговых точек
        delete_similar_points(points_selected)

        return points_selected

    def _modify_signal(self, signal: Signal, left_t: float, right_t: float) -> Signal:
        """
        Создаем "модифицированный" сигнал на основе переданного, исходный сигнал не меняется.
        В дальнейшем в интервале [left_t, right_t] этого сигнала будут искаться особые точки.
        :param signal: сигнал, на основе которого мы делаем модифицированный
        :param left_t: левая граница интервала
        :param right_t: правая граница интервала
        :return: модифицированный сигнал той же длины, что и входной

        :raises PazzleOutOfSignal – если логика пазла потребовала обращения за пределы предоставленного сигнала,
        RunPazzleError – различные ошибки выполнения пазла
        """
        if len(self.rSM_objects) == 0:
            return signal

        modified_signal: Signal = deepcopy(signal)

        for r_SM in self.rSM_objects:
            modified_signal = r_SM.run(modified_signal, left_t=left_t, right_t=right_t)

        assert len(modified_signal) == len(signal), "SM-объекты трека не должны менять длину сигнала"

        return modified_signal

from copy import deepcopy
from itertools import chain
from typing import List

from CORE import Signal
from CORE.db_dataclasses import Track
from CORE.exeptions import RunTrackError, RunPazzleError, PazzleOutOfSignal
from CORE.run.r_ps import R_PS
from CORE.run.r_sm import R_SM
from CORE.visual_debug.results_datcalsses.PS_res import PS_Res
from CORE.visual_debug.results_datcalsses.SM_res import SM_Res
from CORE.visual_debug.results_datcalsses.track_res import TrackRes


class RTrack:
    """Класс для запуска трека на сигнале в заданном месте"""

    def __init__(self, track: Track):
        self.id: int = track.id

        self.rSM_objects: List[R_SM] = [R_SM(base_pazzle=sm) for sm in track.SMs]
        self.rPS_objects: List[R_PS] = [R_PS(base_pazzle=rs) for rs in track.PSs]

    def run(self, signal: Signal, left_t: float, right_t: float) -> TrackRes:
        """
        Основная функция по применению трека к сигналу. Сначала последовательно
        применяет к сигналу объекты SM, и затем к итоговому модифицированному
        ими сигналу применяет (независимые друг от друга) объекты PS.

        Возвращает объект TrackRes с полной информацией о запуске.

        Входной сигнал не изменяется, работа только с deepcopy.

        :param signal: длинный сигнал, на основе которого конструкируется модификация
        :param left_t: левая граница интервала
        :param right_t: правая граница интервала
        :raises RunTrackError, PazzleOutOfSignal

        :return: TrackRes объект с результатами запуска трека
        """
        if len(signal) == 0:
            raise RunTrackError.emty_signal(self.id)

        try:
            # 1. Запускаем SM-объекты в том порядке, в каком они идут в списке
            # и собираем результаты каждого SM
            sm_res_objs = []
            modified_signal = deepcopy(signal)

            for r_sm in self.rSM_objects:
                # Запоминаем сигнал до модификации
                old_signal = modified_signal

                # Запускаем SM и получаем модифицированный сигнал
                result_signal = r_sm.run(old_signal, left_t=left_t, right_t=right_t)

                # Создаем объект с результатом SM
                sm_res = SM_Res(
                    id=r_sm.base_pazzle.id,
                    old_signal=old_signal,
                    result_signal=result_signal,
                    left_coord=left_t,
                    right_coord=right_t
                )
                sm_res_objs.append(sm_res)

                # Обновляем сигнал для следующей итерации
                modified_signal = result_signal

            # 2. Запускаем PS-объекты на измененном сигнале
            ps_res_objs = []
            for r_ps in self.rPS_objects:
                # Запускаем PS и получаем список координат
                points = r_ps.run(modified_signal, left_t, right_t)

                # Создаем объект с результатом PS
                ps_res = PS_Res(
                    id=r_ps.base_pazzle.id,
                    signal=modified_signal,  # все PS видят один и тот же финальный модифицированный сигнал
                    left_coord=left_t,
                    right_coord=right_t,
                    res_coords=points.copy()  # сохраняем исходный список точек
                )
                ps_res_objs.append(ps_res)

            # 3. Проверяем, все ли точки в интервале
            all_points = list(chain.from_iterable(ps_res.res_coords for ps_res in ps_res_objs))
            if any(point < left_t or point > right_t for point in all_points):
                raise RunTrackError.selected_points_out_of_interval(
                    track_id=self.id, right_t=right_t, left_t=left_t
                )

        except RunPazzleError as e:
            raise RunTrackError.internal_problem_in_pazzle(track_id=self.id, error=str(e)) from e
        except PazzleOutOfSignal:
            # не имеет смысла выполнять этот трек, т.к. один из его SM вылез за пределы доступного сигнала.
            # Но это не обязательно аварийная ситуация - поэтому надо переделать наверх, шагу
            raise

        # 4. Создаем и возвращаем TrackRes
        track_res = TrackRes(
            id=self.id,
            signal=signal,
            left_coord=left_t,
            right_coord=right_t,
            ps_res_objs=ps_res_objs,
            sm_res_objs=sm_res_objs
        )

        return track_res

from copy import deepcopy
from typing import Optional, List, Tuple

from CORE import Signal
from CORE.constants import EPSILON_FOR_DUBLES
from CORE.datasets_wrappers.form_associated.parametriser import Parametriser
from CORE.exeptions import RunStepError, PazzleOutOfSignal
from CORE.logger import get_logger
from CORE.run import Exemplar
from CORE.run.r_hc import R_HC
from CORE.run.r_pc import R_PC
from CORE.run.r_track import RTrack
from CORE.run.schema import Schema
from CORE.run.step_interval import Interval
from CORE.visual_debug.results_datcalsses.step_res import StepRes
from CORE.visual_debug.results_datcalsses.track_res import TrackRes

logger = get_logger(__name__)


class RStep:
    """ Класс для запуска одного шага распознавания формы на канкретном сигнале.
    Производит "наращивание" переданного ему экземпляра
    на одну точку (с опутствующей параметризацией).

    При этом, поскольку на данную точку множсетво кандидатов,
     то результатом наращивания станут несколько экземпляров"""

    def __init__(self, interval: Interval, r_tracks: List[RTrack], target_point_name: str, num_in_form: int,
                 schema: Schema,  # добавляем schema
                 rHC_objects: Optional[List[R_HC]] = None, rPC_objects: Optional[List[R_PC]] = None):

        self.num_in_form: int = num_in_form
        self.center: Optional[float] = None

        self.interval: Interval = interval
        self.target_point_name: str = target_point_name

        self.rHC_objects = rHC_objects if rHC_objects is not None else []
        self.rPC_objects = rPC_objects if rPC_objects is not None else []

        self.r_tracks: List[RTrack] = r_tracks
        self.out_of_signal_tracks = 0

        # Создаем параметризатор из схемы
        self.parametriser = Parametriser(schema=schema)

    def set_step_as_first(self, center: float):
        self.center = center

    def get_out_of_signals_procent(self):
        """ В скольки процентах треков произошел выход за пределы предоставленного сигнала"""
        if len(self.r_tracks) == 0:
            return 0.0
        return self.out_of_signal_tracks / len(self.r_tracks)

    def run(self, exemplar: Exemplar) -> Tuple[StepRes, List[Exemplar]]:
        """
        Создает на основе переданного "родительского" экземпляра список экзепляров, каждый из которых на точку длиннее родительского.
        Родительский экзепляр не меняется. Дочерние экземпляры имеют гарантированно разные точки (т.е. дочерние экземпляры прорежены по последней точке)

        Возвращает кортеж (StepRes, List[Exemplar]), где:
        - StepRes содержит полную информацию о запуске шага
        - List[Exemplar] содержит созданные экземпляры (для обратной совместимости)

        :param exemplar: Экземляр формы (в котором выполнены все шаги, предыдущие к данному)
        :raises RunStepError, RunTrackError, RunPazzleError
        :return: Кортеж (StepRes, List[Exemplar])
        """
        if len(self.r_tracks) == 0:
            raise RunStepError.empty_tracks_list(self.num_in_form)
        if not self.target_point_name:
            raise RunStepError.invalid_target_point(self.num_in_form)

        # 1. Получение координат интервала поиска точек на сигнале экземпляра
        left_t, right_t = self.interval.get_interval_coords(center=self.center, exemplar=exemplar)

        # 2. Запускаем по очереди все треки и собираем результаты
        tracks_results, filtered_pairs = self._run_all_tracks(exemplar.signal, left_t=left_t, right_t=right_t)

        if len(filtered_pairs) == 0:
            # Создаем StepRes с пустыми результатами
            step_res = StepRes(id=self.num_in_form, signal=exemplar.signal, left_coord=left_t, right_coord=right_t,
                               tracks_results=tracks_results)
            return step_res, []

        # 3. На основе списка точек-кандидатов (уже профильтрованных от дублей) создаем дочерние экземпляры
        exemplars = self._init_exemplars(exemplar, filtered_pairs)

        # 4. Параметризуем полученные экземпляры
        try:
            for ex in exemplars:
                self.parametriser.parametrise(ex, self.rPC_objects)
        except PazzleOutOfSignal:
            logger.info(
                "PazzleOutOfSignal: параметризация прервана из-за нехватки сигнала одному или нескольким PC шага")
            # Создаем StepRes с результатами треков, но без экземпляров
            step_res = StepRes(id=self.num_in_form, signal=exemplar.signal, left_coord=left_t, right_coord=right_t,
                               tracks_results=tracks_results)
            return step_res, []

        # 5. Удаляем те, которые нарушили жесткие условия на параметры
        exemplars = [ex for ex in exemplars if self.parametriser.fit_conditions(ex, self.rHC_objects)]

        # 6. Создаем StepRes с результатами
        step_res = StepRes(id=self.num_in_form, signal=exemplar.signal, left_coord=left_t, right_coord=right_t,
                           tracks_results=tracks_results)

        return step_res, exemplars

    def _run_all_tracks(self, signal: Signal, left_t: float, right_t: float) -> Tuple[
        List[TrackRes], List[Tuple[int, float]]]:
        """
        Запускает все треки и собирает:
        - список TrackRes для каждого трека
        - отфильтрованные пары (track_id, point) для создания экземпляров

        :return: Кортеж (tracks_results, filtered_pairs)
        """
        tracks_results = []
        all_pairs = []

        # Шаг 1: запускаем все треки и собираем результаты
        for track in self.r_tracks:
            try:
                track_res = track.run(signal, left_t=left_t, right_t=right_t)
                tracks_results.append(track_res)

                # Собираем пары для фильтрации (используем уникальные координаты трека)
                for point in track_res.to_uniq_coords():
                    all_pairs.append((track.id, point))

            except PazzleOutOfSignal:
                # Некоторые треки могли требовать больший фрагмент сигнала для
                # анализа, чем предоставляет данный экземпляр.
                # Такая проблема в одном из треков не является железным показанием к свертыванию шага.
                self.out_of_signal_tracks += 1  # Для треков, вылетевших с PazzleOutOfSignal, не создаем TrackRes

        # Шаг 2: фильтруем близкие точки среди пар
        # Сортируем по значению точки (для удобства сравнения соседних)
        all_pairs.sort(key=lambda pair: pair[1])

        if not all_pairs:
            return tracks_results, []

        filtered_pairs = [all_pairs[0]]  # начинаем с первой пары

        for current_pair in all_pairs[1:]:
            last_kept_point = filtered_pairs[-1][1]
            current_point = current_pair[1]

            # Если текущая точка достаточно удалена от последней сохранённой — добавляем
            if abs(current_point - last_kept_point) >= EPSILON_FOR_DUBLES:
                filtered_pairs.append(current_pair)

        return tracks_results, filtered_pairs

    def _init_exemplars(self, parent_exemplar: Exemplar, filtered_pairs: List[Tuple[int, float]]):
        """
        Создать потомков экземпляра, которые на одну точку больше, чем у предка
        :param parent_exemplar: родительский экземпляр, не меняется в коде
        :param filtered_pairs: список пар вида (id трека , координата точки от этого трека)
        :return:
        """
        exemplars: List[Exemplar] = []

        for track_id, point_coord in filtered_pairs:
            child_exemplar = deepcopy(parent_exemplar)
            child_exemplar.add_point(point_name=self.target_point_name, point_coord_t=point_coord, track_id=track_id)
            exemplars.append(child_exemplar)
            assert len(parent_exemplar) == len(child_exemplar) - 1, "Должно было произойти наращивание на одну точку"

        return exemplars

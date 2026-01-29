from copy import deepcopy
from typing import Optional, List, Tuple

from CORE import Signal
from CORE.constants import EPSILON_FOR_DUBLES
from CORE.exeptions import RunStepError, PazzleOutOfSignal
from CORE.logger import get_logger
from CORE.run import Exemplar
from CORE.run.parametriser import Parametriser
from CORE.run.r_hc import R_HC
from CORE.run.r_pc import R_PC
from CORE.run.r_track import RTrack
from CORE.run.step_interval import Interval

logger = get_logger(__name__)


class RStep:
    """ Класс для запуска одного шага распознавания формы на канкретном сигнале.
    Производит "наращивание" переданного ему экземпляра
    на одну точку (с опутствующей параметризацией).

    При этом, поскольку на данную точку множсетво кандидатов,
     то результатом наращивания станут несколько экземпляров"""

    def __init__(self, interval: Interval, r_tracks: List[RTrack], target_point_name: str, num_in_form: int,
                 center: Optional[float] = None, rHC_objects: Optional[List[R_HC]] = None,
                 rPC_objects: Optional[List[R_PC]] = None):
        self.num_in_form: int = num_in_form
        self.center = center

        self.interval: Interval = interval
        self.target_point_name: str = target_point_name

        self.rHC_objects = rHC_objects if rHC_objects is not None else []
        self.rPC_objects = rPC_objects if rPC_objects is not None else []

        self.r_tracks: List[RTrack] = r_tracks
        self.out_of_signal_tracks = 0

    def get_out_of_signals_procent(self):
        """ В скольки процентах треков произошел выход за пределы предоставленного сигнала"""
        return self.out_of_signal_tracks / len(self.r_tracks)

    def run(self, exemplar: Exemplar) -> List[Exemplar]:
        """
        Создает на основе переданного "родительского" экземпляра список экзепляров, каждый из которыз на точку длиннее родительского.
        Родительский экзепляр не меняется. Дочерние экземпляры имеют гарантированно разные точки (т.е. дочерние экземпляры прорежены по последней точке)

        :param exemplar: Экземляр формы (в котором выполнены все шаги, предыдущие к данному)
        :raises RunStepError, RunTrackError, RunPazzleError
        :return: Список экземпляров, в каждом из которых на одну точку больше, чем в "родительском"
        """
        if len(self.r_tracks) == 0:
            raise RunStepError.empty_tracks_list(self.num_in_form)
        if not self.target_point_name:
            raise RunStepError.invalid_target_point(self.num_in_form)

        # 1. Получением координаты инфтервала поиска точек на сигнале экземпляра
        left_t, right_t = self.interval.get_interval_coords(center=self.center, exemplar=exemplar)

        # 2. Запускаем по очереди все треки, получаем пары  вида track_id:одна_из_результирующих_точек
        filtered_pairs = self._run_all_tracks(exemplar.signal, left_t=left_t, right_t=right_t)

        if len(filtered_pairs) == 0:
            return []  # возможны две причины такого исхода: искомых точек дейтсвительно нет или длины сигнала недостаточно для анализа

        # 3. На основе списка точек-кандидатов (уже профильтрованных от дублей) создаем дочерние экземпляры
        exemplars = self._init_exemplars(exemplar, filtered_pairs)

        # 4. Параметризуем полученные экземпляры
        parametriser = Parametriser()
        try:
            for exemplar in exemplars:
                parametriser.parametrise(exemplar, r_pcs=self.rPC_objects)
        except PazzleOutOfSignal:
            logger.info(
                "PazzleOutOfSignal: параметризация прервана из-за нехватки сигнала одному или нескольким PC шага")
            return []

        # 5. Удялаяем те, которые нарушили жесткие условия на параметры
        exemplars = [ex for ex in exemplars if parametriser.fit_conditions(ex, self.rHC_objects)]

        return exemplars

    def _run_all_tracks(self, signal: Signal, left_t: float, right_t: float) -> List[Tuple[int, float]]:
        """
            Собирает пары (track_id, point) из всех треков, удаляя точки,
            которые находятся ближе друг к другу чем EPSILON_FOR_DUBLES.


            :return: Список кортежей (track_id: int, point: float)
            """
        all_pairs = []

        # Шаг 1: собираем все пары (id, point)
        for track in self.r_tracks:
            try:
                selected_points = track.run(signal, left_t=left_t, right_t=right_t)
                for point in selected_points:
                    all_pairs.append((track.id, point))
            except PazzleOutOfSignal:
                # Некоторые треки могли требовать больший врагмент сигнала для
                # анализа, чем предодставляет данный экземпляр.
                # Такая проблема в одном из треков не является железным показанием к свертыванию шага.
                self.out_of_signal_tracks += 1

        # Шаг 2: фильтруем близкие точки
        # Сортируем по значению точки (для удобства сравнения соседних)
        all_pairs.sort(key=lambda pair: pair[1])

        filtered_pairs = [all_pairs[0]]  # начинаем с первой пары

        for current_pair in all_pairs[1:]:
            last_kept_point = filtered_pairs[-1][1]
            current_point = current_pair[1]

            # Если текущая точка достаточно удалена от последней сохранённой — добавляем
            if abs(current_point - last_kept_point) >= EPSILON_FOR_DUBLES:
                filtered_pairs.append(current_pair)

        return filtered_pairs

    def _init_exemplars(self, parent_exemplar: Exemplar, filtered_pairs: List[Tuple[int, float]]):
        """
        Создать потомков экземпляра, которые на одну точку больше, чем у предка
        :param parent_exemplar: родительский экземпляр, не меняется в коде
        :param filtered_pairs: списов пар вида (id трека , коррдината точки от этого трека)
        :return:
        """
        exemplars: List[Exemplar] = []

        for track_id, point_coord in filtered_pairs:
            child_exemplar = deepcopy(parent_exemplar)
            child_exemplar.add_point(point_name=self.target_point_name, point_coord_t=point_coord, track_id=track_id)
            exemplars.append(child_exemplar)
            assert len(parent_exemplar) == len(child_exemplar) - 1, "Должно было произойти наращивание на одну точку"

        return exemplars

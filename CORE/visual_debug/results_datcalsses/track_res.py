from dataclasses import dataclass
from typing import Dict, List

from CORE import Signal
from CORE.run.utils import delete_similar_points
from CORE.visual_debug.results_datcalsses.PS_res import PS_Res
from CORE.visual_debug.results_datcalsses.SM_res import SM_Res


@dataclass
class TrackRes:
    id: int  # id трека в базе

    signal: Signal  # исходный сигнал экземпляра ДО запуска SM этого трека
    left_coord: float  # левая координата, заданная в настройках шага, которому принадлежит этот трек
    right_coord: float  # правая. Вместе с левой ограничивает интервал, на котором шаг допускает поиск целевой точки

    ps_res_objs: List[PS_Res]
    sm_res_objs: List[SM_Res]  # порядок важен

    def get_ps_coords_by_id(self) -> Dict[int, List[float]]:
        """ Возвращает словарь, где ключ - id PS-объекта, значение - его res_coords. """
        return {ps_obj.id: ps_obj.res_coords for ps_obj in self.ps_res_objs}

    def get_sm_modifications_seq(self) -> List[Signal]:
        """ Возвращает список последовательных модификаций сигнала, их кол-во = кол-ву SM в треке """
        return [sm_obj.result_signal for sm_obj in self.sm_res_objs]

    def get_all_ps_coords_flat(self) -> List[float]:
        """ Возвращает объединенный список всех res_coords из всех PS-объектов. """
        result = []
        for ps_obj in self.ps_res_objs:
            result.extend(ps_obj.res_coords)
        return result

    def to_uniq_coords(self) -> List[float]:
        """
        Возвращает список уникальных координат, найденных всеми PS в этом треке.
        Дубли удаляются с помощью delete_similar_points.
        """
        all_coords = self.get_all_ps_coords_flat()
        delete_similar_points(all_coords)  # модифицируем список на месте
        return all_coords  # возвращаем тот же список

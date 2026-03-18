from dataclasses import dataclass
from typing import Dict, List

from CORE import Signal
from CORE.visual_debug.results_datcalsses.track_res import TrackRes


@dataclass
class StepRes:
    id: int  # id шага в БД

    signal: Signal  # исходный сигнал экземпляра
    left_coord: float  # левая координата, заданная в настройках этого шага
    right_coord: float  # правая. Вместе с левой ограничивает интервал, на котором шаг допускает поиск целевой точки

    tracks_results: List[TrackRes]

    def get_tracks_results(self) -> Dict[int, List[float]]:
        """ Возвращает словарь, где ключ - id трека, значение - найденные этим треком точки (с дублями) """
        return {track_obj.id: track_obj.get_all_ps_coords_flat() for track_obj in self.tracks_results}

    def get_tracks_uniq_results(self) -> Dict[int, List[float]]:
        """ Возвращает словарь, где ключ - id трека, значение - уникальные точки, найденные этим треком """
        return {track_obj.id: track_obj.to_uniq_coords() for track_obj in self.tracks_results}

    def get_all_points_flat(self) -> List[float]:
        """ Возвращает объединенный список всех точек из всех треков (с дублями) """
        result = []
        for track_obj in self.tracks_results:
            result.extend(track_obj.get_all_ps_coords_flat())
        return result

    def to_uniq_coords(self) -> List[float]:
        """
        Возвращает список уникальных координат, найденных всеми треками в этом шаге.
        Дубли удаляются с помощью delete_similar_points.
        """
        from CORE.run.utils import delete_similar_points
        all_coords = self.get_all_points_flat()
        delete_similar_points(all_coords)
        return all_coords

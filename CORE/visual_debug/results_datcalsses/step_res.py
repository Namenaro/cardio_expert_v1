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
        """ Возвращает словарь, где ключ - id трека, значение - найденные этим треком точки """
        return {track_obj.id: track_obj.get_all_ps_coords_flat() for track_obj in self.tracks_results}

"""Утилиты для работы симулятора"""

from typing import Optional, Tuple, Union
from CORE.db_dataclasses import Form, Step
from CORE.run.step_interval import Interval
from CORE.visual_debug.results_datcalsses.track_res import TrackRes
from CORE.exeptions import PazzleOutOfSignal
from CORE.run.r_track import RTrack
from CORE.run import Exemplar
from CORE.logger import get_logger

logger = get_logger(__name__)


def find_track(form: Form, track_id: int) -> Optional[Tuple]:
    """Находит трек по ID во всех шагах формы"""
    for step in form.steps:
        for track in step.tracks:
            if track.id == track_id:
                return track, step
    return None


def make_interval(step: Step) -> Union[Interval, str]:
    """Создает Interval из шага"""
    try:
        interval = Interval()
        if step.left_point:
            interval.set_point_left(step.left_point.name)
        elif step.left_padding_t is not None:
            interval.set_left_padding(step.left_padding_t)

        if step.right_point:
            interval.set_point_right(step.right_point.name)
        elif step.right_padding_t is not None:
            interval.set_right_padding(step.right_padding_t)

        return interval if interval.validate() else f"Интервал шага {step.num_in_form} некорректен"
    except Exception as e:
        return f"Ошибка интервала: {e}"


def get_coords(interval: Interval, exemplar: Exemplar, center: Optional[float] = None) -> Union[
    Tuple[float, float], str]:
    """Безопасно получает координаты интервала"""
    try:
        left, right = interval.get_interval_coords(exemplar, center)
        logger.debug(f"Интервал: [{left:.3f}, {right:.3f}]")
        return left, right
    except Exception as e:
        return f"Ошибка вычисления координат: {e}"


def exec_track(track, signal, left: float, right: float, track_id: int) -> Union[TrackRes, str]:
    """Запускает трек на сигнале"""
    try:
        logger.debug(f"Запуск трека {track_id} на интервале [{left:.3f}, {right:.3f}]")

        r_track = RTrack(track)
        result = r_track.run(signal, left, right)

        return result
    except PazzleOutOfSignal:
        # Это штатная ситуация, не ошибка
        msg = f"Трек {track_id} вышел за пределы сигнала"
        logger.info(msg)
        return msg
    except Exception as e:
        # Логируем один раз с полным трейсбеком
        logger.error(f"Ошибка трека {track_id}: {e}", exc_info=True)
        # Возвращаем только сообщение, без трейсбека
        return f"Ошибка трека {track_id}: {e}"

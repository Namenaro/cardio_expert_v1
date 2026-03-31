"""Утилиты для работы симулятора"""
import copy
from typing import Optional, Set
from typing import Tuple, Union

from CORE.datasets_wrappers.form_associated.parametriser import Parametriser
from CORE.db_dataclasses import Form, Step
from CORE.exeptions import PazzleOutOfSignal
from CORE.logger import get_logger
from CORE.run.exemplar import Exemplar
from CORE.run.r_form import RForm
from CORE.run.r_hc import R_HC
from CORE.run.r_pc import R_PC
from CORE.run.r_track import RTrack
from CORE.run.step_interval import Interval
from CORE.visual_debug.results_datcalsses.track_res import TrackRes

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


def create_snapshot_from_step(
        exemplar: Exemplar,
        step_num: int,
        rform: RForm,
        include_current_step: bool
) -> Optional[Exemplar]:
    """
    Создает глубокую копию экземпляра, удаляя все точки начиная с указанного шага,
    затем очищает все параметры, HC и оценку, после чего запускает параметризацию
    заново для оставшихся точек.

    :param exemplar: исходный экземпляр
    :param step_num: номер шага (начиная с 0), начиная с которого нужно удалить точки
    :param rform: объект RForm, содержащий информацию о шагах и их HC/PC
    :param include_current_step: удалять ли точки текущего шага (True - удаляем, False - сохраняем)
    :return: новый экземпляр Exemplar с пересчитанными параметрами, или None, если шаг не найден
    """
    # Проверяем, что шаг с таким номером существует в форме
    if step_num < 0 or step_num >= len(rform.form.steps):
        logger.error(f"Шаг {step_num} не найден в форме. Всего шагов: {len(rform.form.steps)}")
        return None

    # Создаем глубокую копию текущего экземпляра
    snapshot = copy.deepcopy(exemplar)

    # Определяем стартовый индекс для удаления точек
    start_idx = step_num if include_current_step else step_num + 1

    # 1. Удаляем точки начиная с указанного шага
    points_to_remove: Set[str] = set()
    for step in rform.form.steps[start_idx:]:
        if step.target_point and step.target_point.name:
            points_to_remove.add(step.target_point.name)

    for point_name in points_to_remove:
        if point_name in snapshot._points:
            del snapshot._points[point_name]

    logger.info(f"Удалено точек: {len(points_to_remove)}")

    # 2. Очищаем все параметры, HC и оценку
    snapshot._parameters.clear()
    snapshot.passed_HCs_ids = []
    snapshot.failed_HCs_ids = []
    snapshot.evaluation_result = None

    # 3. Определяем последний шаг, который остался в снимке
    # Если include_current_step = True, то остались шаги до step_num (не включая step_num)
    # Если include_current_step = False, то остались шаги до step_num (включая step_num)
    last_step = step_num - 1 if include_current_step else step_num

    # Если last_step < 0, значит не осталось ни одного шага
    if last_step < 0:
        logger.warning("В снимке не осталось ни одной точки")
        return snapshot

    # 4. Запускаем параметризацию заново для оставшихся шагов
    try:
        parametriser = Parametriser(schema=rform.schema)

        # Применяем PC для всех шагов до last_step включительно
        for step_idx in range(last_step + 1):
            base_pcs = rform.schema.get_PCs_by_step_num(step_idx)
            if base_pcs:
                r_pcs = [
                    R_PC(
                        base_pazzle=pc,
                        form_points=rform.form.points,
                        form_params=rform.form.parameters
                    )
                    for pc in base_pcs
                ]
                parametriser.parametrise(snapshot, r_pcs)
                logger.debug(f"Применены {len(r_pcs)} PC для шага {step_idx}")

        # Создаем R_HC объекты только для HC, которые относятся к оставшимся шагам
        hc_ids_to_check: Set[int] = set()
        for step_idx in range(last_step + 1):
            base_hcs = rform.schema.get_HCs_by_step_num(step_idx)
            for hc in base_hcs:
                if hc.id is not None:
                    hc_ids_to_check.add(hc.id)

        r_hcs = [
            R_HC(pazzle, form_params=rform.form.parameters)
            for pazzle in rform.form.HC_PC_objects
            if pazzle.is_HC() and pazzle.id in hc_ids_to_check
        ]

        if r_hcs:
            parametriser.fit_conditions(snapshot, r_hcs)
            logger.debug(f"Проверены HC для шагов 0-{last_step}")


    except Exception as e:
        logger.error(f"Ошибка при параметризации снимка: {e}")
        return None

    logger.info(f"Создан снимок экземпляра {exemplar.id} начиная с шага {step_num} "
                f"(включая текущий: {include_current_step})")

    return snapshot

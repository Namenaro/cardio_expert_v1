from __future__ import annotations

from typing import List

from CORE import Signal
from CORE.db_dataclasses import BasePazzle
from CORE.exeptions import RunPazzleError, PazzleOutOfSignal
from CORE.pazzles_lib.ps_base import PSBase

from CORE.run.run_pazzle import PazzleParser
from CORE.run.utils import delete_simialr_points


class R_PS:
    def __init__(self, base_pazzle: BasePazzle):
        """
        Инициализация из класса, служащего (де)сериализаци из БД.

        :param base_pazzle: базовый пазл (описание класса пазла)

        """
        self.base_pazzle = base_pazzle

    def run(self, signal: Signal, left_t: float, right_t: float) -> List[float]:
        """
        Основной метод выполнения пазла на конкретном сигнале.
        Сигнал идет вместе с интервалом, в котором и только в котором может выбирать точки

        Создает и запускает rannable объект пазла
        :param signal взодной сигнал
        :param left_t левая граница интервала а
        :param right_t правая граница интервала


        :raise PazzleOutOfSignal: если логика пазла потребовала обращения за пределы предоставленного сигнала
        :raise RunPazzleError: различные ошибки выполнения пазла
        :return список координат "особых" (отобранных этим пазлом) точек
        """
        parser = PazzleParser(self.base_pazzle, form_points=[], form_params=[])

        # Создание runnable-объекта
        runnable = self._create_runnable(parser)

        # Запуск и получение результата
        selected_points = self._execute_runnable(runnable, signal, left_t=left_t, right_t=right_t)

        # проверим, все ли выбранные точки попали в допустимый интервал
        for point in selected_points:
            if point < left_t or point > right_t:
                raise RunPazzleError.selected_point_out_of_interval(left_t=left_t,
                                                                    right_t=right_t,
                                                                    point=point,
                                                                    class_name=self.base_pazzle.class_ref.name,
                                                                    pazzle_id=self.base_pazzle.id)
        delete_simialr_points(selected_points)
        return selected_points

    def _create_runnable(self, parser: PazzleParser) -> PSBase:
        """
        Создает экземпляр класса пазла (runnable-объект).

        :param parser: объект парсера для получения информации о классе пазла
        :raise RunPazzleError: если не удалось создать экземпляр класса
        :return Экземпляр класса пазла
        """
        try:
            cls = parser.get_cls()
            args = parser.get_constructor_arguments()
            return cls(**args)
        except Exception as e:
            raise RunPazzleError.class_creation_failed(self.base_pazzle.id, str(e))

    def _execute_runnable(self, runnable: PSBase, signal: Signal, left_t: float, right_t: float) -> List[float]:
        """
        Запускает выполнение runnable-объекта на сигнале.

        :param runnable: экземпляр класса пазла для выполнения
        :param signal: сигнал для обработки
        :raise PazzleOutOfSignal: если пазл запросил данные за пределами сигнала
        :raise RunPazzleError: другие ошибки выполнения пазла
        :return Словарь с результатами измерений
        """
        try:
            return runnable.run(signal, left_t=left_t, right_t=right_t)
        except PazzleOutOfSignal as e:
            # Дописываем имя класса и пробрасываем дальше
            if not e.class_name:
                e.class_name = self.base_pazzle.class_ref.name
            raise
        except Exception as e:
            class_name = self.base_pazzle.class_ref.name
            raise RunPazzleError.execution_error(self.base_pazzle.id, class_name, str(e))

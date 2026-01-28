from __future__ import annotations

import logging
from typing import Dict, Any, List, Tuple, Optional

from CORE import Signal
from CORE.db_dataclasses import BasePazzle, Point, Parameter
from CORE.exeptions import RunPazzleError, PazzleOutOfSignal
from CORE.pazzles_lib.pc_base import PCBase
from CORE.pazzles_lib.sm_base import SMBase
from CORE.run import Exemplar
from CORE.run.run_pazzle import PazzleParser

logger = logging.getLogger(__name__)


class R_SM:
    def __init__(self, base_pazzle: BasePazzle):
        """
        Инициализация экземпляра R_PC из класса, служащего (де)сериализаци из БД.

        :param base_pazzle: базовый пазл (описание класса пазла)

        """
        self.base_pazzle = base_pazzle

    def run(self, signal: Signal, left_t: float, right_t: float) -> Signal:
        """
        Основной метод выполнения пазла на конкретном сигнале.

        Создает и запускает rannable объект пазла

        :param exemplar: экземпляр формы для обработки
        :raise PazzleOutOfSignal: если логика пазла потребовала обращения за пределы предоставленного сигнала
        :raise RunPazzleError: различные ошибки выполнения пазла
        :return модифицированный сигнал той же длины
        """
        parser = PazzleParser(self.base_pazzle, form_points=[], form_params=[])

        # Создание runnable-объекта
        runnable = self._create_runnable(parser)

        # Запуск и получение результата
        new_signal = self._execute_runnable(runnable, signal, left_t=left_t, right_t=right_t)

        if len(signal) != len(new_signal):
            logger.exception(
                f"SM-объект {self.base_pazzle.id} изменил длину сигнала на {len(signal) - len(new_signal)} секунд ")
            raise RunPazzleError.sm_changed_len_of_signal(delta_time=(len(signal) - len(new_signal)),
                                                          class_name=self.base_pazzle.class_ref.name,
                                                          pazzle_id=self.base_pazzle.id)
        return new_signal

    def _create_runnable(self, parser: PazzleParser) -> SMBase:
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
            logger.exception(f"Ошибка создания экземпляра SM пазла {self.base_pazzle.id}: {e}")
            raise RunPazzleError.class_creation_failed(self.base_pazzle.id, str(e))

    def _execute_runnable(self, runnable: SMBase, signal: Signal, left_t: float, right_t: float) -> Signal:
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
            logger.warning(f"Пазл {e.class_name} запросил данные за пределами сигнала: {e.message}")
            raise
        except Exception as e:
            logger.exception(f"Внутренняя ошибка при выполнении пазла {self.base_pazzle.id}: {e}")
            class_name = self.base_pazzle.class_ref.name
            raise RunPazzleError.execution_error(self.base_pazzle.id, class_name, str(e))

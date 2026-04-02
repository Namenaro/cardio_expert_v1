# DA3/simulation_app/simulator_controller.py

import logging
from typing import Optional

from PySide6.QtCore import QObject

from CORE.db_dataclasses import Form
from CORE.run import Exemplar
from CORE.visual_debug import TrackRes, StepRes, SM_Res, PS_Res
from DA3 import app_signals
from DA3.simulation_app.main_window import MainFormSimulator
from DA3.simulation_app.simulator import Simulator
from DA3.simulation_app.simulator_signals import get_signals

logger = logging.getLogger(__name__)


class SimulatorController(QObject):
    def __init__(self, form: Optional[Form] = None):
        super().__init__()
        self.main_window: Optional[MainFormSimulator] = None
        self.simulator = Simulator()

        # Для хранения текущего выбранного элемента
        self.current_track_id: Optional[int] = None
        self.current_step_id: Optional[int] = None
        self.current_sm_id: Optional[int] = None
        self.current_ps_id: Optional[int] = None

        # Получаем глобальные сигналы
        self.signals = get_signals()

        # Подключаем сигналы
        self._connect_signals()

        if form:
            self.simulator.reset_form(form)
        app_signals.form.form_changed.connect(self.on_form_changed)

    def _connect_signals(self):
        """Подключает сигналы к обработчикам"""
        self.signals.track_selected.connect(self.on_track_selected)
        self.signals.step_selected.connect(self.on_step_selected)
        self.signals.SM_selected.connect(self.on_sm_selected)
        self.signals.PS_selected.connect(self.on_ps_selected)
        self.signals.requested_next.connect(self.on_next_requested)
        self.signals.requested_prev.connect(self.on_prev_requested)
        self.signals.full_simulate_requested.connect(self.on_full_simulate_requested)
        self.signals.full_simulate_extended_requested.connect(self.on_full_simulate_extended_requested)
        self.signals.clear_selection_requested.connect(self.on_clear_selection)

    def on_form_changed(self, form: Form):
        """Обработчик смены формы"""
        self.simulator.reset_form(form)
        self.current_track_id = None
        self.current_step_id = None
        self.current_sm_id = None
        self.current_ps_id = None
        if self.main_window:
            self.main_window.update_form(self.get_r_form())
            self._init_first_exemplar()

    def _init_first_exemplar(self):
        """Инициализирует первый экземпляр датасета"""
        exemplar = self.simulator.next()
        if exemplar and self.main_window:
            self.main_window.show_exemplar(exemplar)
            self.main_window.set_example_id(str(exemplar.id))
            self.main_window.set_navigation_buttons_enabled(
                prev_enabled=False,
                next_enabled=self.simulator.has_next()
            )
            self.current_track_id = None
            self.current_step_id = None
            self.current_sm_id = None
            self.current_ps_id = None

    def on_step_selected(self, step_id: int, num_in_form: int):
        """Обработчик выбора шага"""
        logger.debug(f"Выбран шаг: id={step_id}, num_in_form={num_in_form}")

        # Сохраняем выбранный шаг и сбрасываем другие
        self.current_step_id = step_id
        self.current_track_id = None
        self.current_sm_id = None
        self.current_ps_id = None

        # Получаем текущий экземпляр
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            self.signals.error_occurred.emit("Нет текущего экземпляра для симуляции")
            if self.main_window:
                self.main_window.show_empty("Нет текущего экземпляра для симуляции")
            return

        # Запускаем шаг
        result = self.simulator.run_step(current_exemplar, step_id)

        if isinstance(result, str):
            # Ошибка
            logger.error(f"Ошибка при выполнении шага {step_id}: {result}")
            if self.main_window:
                self.main_window.show_empty(result)
        else:
            # Успех - показываем результат
            step_res: StepRes = result
            if self.main_window:
                self.main_window.show_step(step_res)

    def on_track_selected(self, track_id: int):
        """Обработчик выбора трека"""
        logger.debug(f"Выбран трек: id={track_id}")

        # Сохраняем выбранный трек и сбрасываем другие
        self.current_track_id = track_id
        self.current_step_id = None
        self.current_sm_id = None
        self.current_ps_id = None

        # Получаем текущий экземпляр
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            self.signals.error_occurred.emit("Нет текущего экземпляра для симуляции")
            if self.main_window:
                self.main_window.show_empty("Нет текущего экземпляра для симуляции")
            return

        # Запускаем трек
        result = self.simulator.run_track(current_exemplar, track_id)

        if isinstance(result, str):
            # Ошибка
            logger.error(f"Ошибка при выполнении трека {track_id}: {result}")
            if self.main_window:
                self.main_window.show_empty(result)
        else:
            # Успех - показываем результат
            track_res: TrackRes = result
            if self.main_window:
                self.main_window.show_track(track_res)

    def on_sm_selected(self, sm_id: int):
        """Обработчик выбора SM-пазла"""
        logger.debug(f"Выбран SM: id={sm_id}")

        # Сохраняем выбранный SM и сбрасываем другие
        self.current_sm_id = sm_id
        self.current_track_id = None
        self.current_step_id = None
        self.current_ps_id = None

        # Получаем текущий экземпляр
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            self.signals.error_occurred.emit("Нет текущего экземпляра для симуляции")
            if self.main_window:
                self.main_window.show_empty("Нет текущего экземпляра для симуляции")
            return

        # Запускаем SM
        result = self.simulator.run_SM(current_exemplar, sm_id)

        if isinstance(result, str):
            # Ошибка
            logger.error(f"Ошибка при выполнении SM {sm_id}: {result}")
            if self.main_window:
                self.main_window.show_empty(result)
        else:
            # Успех - показываем результат
            sm_res: SM_Res = result
            if self.main_window:
                self.main_window.show_sm(sm_res)

    def on_ps_selected(self, ps_id: int):
        """Обработчик выбора PS-пазла"""
        logger.debug(f"Выбран PS: id={ps_id}")

        # Сохраняем выбранный PS и сбрасываем другие
        self.current_ps_id = ps_id
        self.current_track_id = None
        self.current_step_id = None
        self.current_sm_id = None

        # Получаем текущий экземпляр
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            self.signals.error_occurred.emit("Нет текущего экземпляра для симуляции")
            if self.main_window:
                self.main_window.show_empty("Нет текущего экземпляра для симуляции")
            return

        # Получаем ground truth точку для PS (если есть)
        ground_true_point = self._get_ground_truth_for_ps(current_exemplar, ps_id)

        # Запускаем PS
        result = self.simulator.run_PS(current_exemplar, ps_id)

        if isinstance(result, str):
            # Ошибка
            logger.error(f"Ошибка при выполнении PS {ps_id}: {result}")
            if self.main_window:
                self.main_window.show_empty(result)
        else:
            # Успех - показываем результат
            ps_res: PS_Res = result
            if self.main_window:
                self.main_window.show_ps(ps_res, ground_true_point)

    def on_full_simulate_requested(self):
        """Обработчик запроса полной симуляции формы (стандартный вид)"""
        logger.debug("Запрошена полная симуляция формы (стандартный вид)")

        # Сбрасываем выбранные элементы
        self.current_track_id = None
        self.current_step_id = None
        self.current_sm_id = None
        self.current_ps_id = None

        # Получаем текущий экземпляр для сигнала
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            self.signals.error_occurred.emit("Нет текущего экземпляра для симуляции")
            if self.main_window:
                self.main_window.show_empty("Нет текущего экземпляра для симуляции")
            return

        # Получаем сигнал и семинальную точку (середина сигнала)
        signal = current_exemplar.get_signal()
        seminal_point = signal.get_duration() / 2

        # Запускаем форму
        result = self.simulator.run_form(signal, seminal_point)

        if isinstance(result, str):
            # Ошибка
            logger.error(f"Ошибка при выполнении формы: {result}")
            if self.main_window:
                self.main_window.show_empty(result)
        else:
            # Успех - показываем результат в стандартном виджете
            pool = result

            ground_truth = self.simulator.get_current_exemplar()
            if self.main_window:
                self.main_window.show_form(pool, ground_truth)
                logger.info(f"Форма выполнена успешно. Показано {len(pool)} экземпляров")

    def on_full_simulate_extended_requested(self):
        """Обработчик запроса полной симуляции формы (расширенный вид - все экземпляры по отдельности)"""
        logger.debug("Запрошена полная симуляция формы (расширенный вид)")

        # Сбрасываем выбранные элементы
        self.current_track_id = None
        self.current_step_id = None
        self.current_sm_id = None
        self.current_ps_id = None

        # Получаем текущий экземпляр для сигнала
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            self.signals.error_occurred.emit("Нет текущего экземпляра для симуляции")
            if self.main_window:
                self.main_window.show_empty("Нет текущего экземпляра для симуляции")
            return

        # Получаем сигнал и семинальную точку (середина сигнала)
        signal = current_exemplar.get_signal()
        seminal_point = signal.get_duration() / 2

        # Запускаем форму
        result = self.simulator.run_form(signal, seminal_point)

        if isinstance(result, str):
            # Ошибка
            logger.error(f"Ошибка при выполнении формы: {result}")
            if self.main_window:
                self.main_window.show_empty(result)
        else:
            # Успех - показываем результат в расширенном виджете
            pool = result
            # Получаем ground truth из текущего экземпляра
            ground_truth = self.simulator.get_current_exemplar()
            if self.main_window:
                self.main_window.show_form_extended(pool, ground_truth)
                logger.info(f"Форма выполнена успешно. Показано {len(pool)} экземпляров в расширенном виде")

    def on_clear_selection(self):
        """Обработчик снятия выделения"""
        logger.debug("Снятие выделения")

        # Сбрасываем выбранные элементы
        self.current_track_id = None
        self.current_step_id = None
        self.current_sm_id = None
        self.current_ps_id = None

        # Показываем текущий экземпляр
        current_exemplar = self.simulator.get_current_exemplar()
        if current_exemplar and self.main_window:
            self.main_window.show_exemplar(current_exemplar)
            logger.debug("Показан текущий экземпляр")

    def _update_current_content(self):
        """Обновляет текущий контент для нового экземпляра"""
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            return

        # Если есть выбранный SM - обновляем его результат
        if self.current_sm_id is not None:
            logger.debug(f"Обновляем SM {self.current_sm_id} для нового экземпляра")
            result = self.simulator.run_SM(current_exemplar, self.current_sm_id)

            if isinstance(result, str):
                logger.error(f"Ошибка при обновлении SM {self.current_sm_id}: {result}")
                if self.main_window:
                    self.main_window.show_empty(result)
            else:
                sm_res: SM_Res = result
                if self.main_window:
                    self.main_window.show_sm(sm_res)

        # Если есть выбранный PS - обновляем его результат
        elif self.current_ps_id is not None:
            logger.debug(f"Обновляем PS {self.current_ps_id} для нового экземпляра")

            # Получаем ground truth точку для PS
            ground_true_point = self._get_ground_truth_for_ps(current_exemplar, self.current_ps_id)

            result = self.simulator.run_PS(current_exemplar, self.current_ps_id)

            if isinstance(result, str):
                logger.error(f"Ошибка при обновлении PS {self.current_ps_id}: {result}")
                if self.main_window:
                    self.main_window.show_empty(result)
            else:
                ps_res: PS_Res = result
                if self.main_window:
                    self.main_window.show_ps(ps_res, ground_true_point)

        # Если есть выбранный шаг - обновляем его результат
        elif self.current_step_id is not None:
            logger.debug(f"Обновляем шаг {self.current_step_id} для нового экземпляра")
            result = self.simulator.run_step(current_exemplar, self.current_step_id)

            if isinstance(result, str):
                logger.error(f"Ошибка при обновлении шага {self.current_step_id}: {result}")
                if self.main_window:
                    self.main_window.show_empty(result)
            else:
                step_res: StepRes = result
                if self.main_window:
                    self.main_window.show_step(step_res)

        # Если есть выбранный трек - обновляем его результат
        elif self.current_track_id is not None:
            logger.debug(f"Обновляем трек {self.current_track_id} для нового экземпляра")
            result = self.simulator.run_track(current_exemplar, self.current_track_id)

            if isinstance(result, str):
                logger.error(f"Ошибка при обновлении трека {self.current_track_id}: {result}")
                if self.main_window:
                    self.main_window.show_empty(result)
            else:
                track_res: TrackRes = result
                if self.main_window:
                    self.main_window.show_track(track_res)

        else:
            # Нет выбранного элемента - показываем экземпляр
            if self.main_window:
                self.main_window.show_exemplar(current_exemplar)

    def on_next_requested(self):
        """Обработчик запроса следующего экземпляра"""
        logger.debug("Запрошен следующий экземпляр")

        exemplar = self.simulator.next()
        if exemplar and self.main_window:
            self.main_window.set_example_id(str(exemplar.id))
            self.main_window.set_navigation_buttons_enabled(
                prev_enabled=True,
                next_enabled=self.simulator.has_next()
            )
            # Обновляем текущий контент (сохраняя тип виджета)
            self._update_current_content()
        else:
            logger.warning("Нет следующего экземпляра")

    def on_prev_requested(self):
        """Обработчик запроса предыдущего экземпляра"""
        logger.debug("Запрошен предыдущий экземпляр")

        exemplar = self.simulator.prev()
        if exemplar and self.main_window:
            self.main_window.set_example_id(str(exemplar.id))
            self.main_window.set_navigation_buttons_enabled(
                prev_enabled=self.simulator.has_prev(),
                next_enabled=True
            )
            # Обновляем текущий контент (сохраняя тип виджета)
            self._update_current_content()
        else:
            logger.warning("Нет предыдущего экземпляра")

    def _get_ground_truth_for_ps(self, exemplar: Exemplar, ps_id: int) -> Optional[float]:
        """
        Получает ground truth точку для PS.
        PS обычно связан с определенным шагом, ищет целевую точку этого шага.
        """
        if not self.simulator.rform:
            return None

        # Находим трек, содержащий этот PS
        found = self.simulator.rform.find_track_by_ps_id(ps_id)
        if not found:
            return None

        step_idx, _ = found

        # Получаем шаг
        if step_idx >= len(self.simulator.rform.rsteps):
            return None

        rstep = self.simulator.rform.rsteps[step_idx]
        target_point_name = rstep.target_point_name

        # Получаем координату целевой точки из экземпляра
        if target_point_name:
            coord = exemplar.get_point_coord(target_point_name)
            if coord is not None:
                return coord

        return None



    def get_r_form(self):
        return self.simulator.rform

    def run(self):
        logger.info("Показываем окно симулятора")
        self.main_window = MainFormSimulator(r_form=self.get_r_form())
        self.main_window.show()
        self._init_first_exemplar()
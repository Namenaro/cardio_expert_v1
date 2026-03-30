# DA3/simulation_app/simulator_controller.py

import logging
from typing import Optional

from PySide6.QtCore import QObject

from CORE.db_dataclasses import Form
from CORE.visual_debug import TrackRes
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
        self.signals.requested_next.connect(self.on_next_requested)
        self.signals.requested_prev.connect(self.on_prev_requested)
        self.signals.clear_selection_requested.connect(self.on_clear_selection)

    def on_form_changed(self, form: Form):
        """Обработчик смены формы"""
        self.simulator.reset_form(form)
        self.current_track_id = None  # Сбрасываем выбранный трек
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
            self.current_track_id = None  # Сбрасываем выбранный трек

    def on_track_selected(self, track_id: int):
        """Обработчик выбора трека"""
        logger.debug(f"Выбран трек: id={track_id}")

        # Сохраняем выбранный трек
        self.current_track_id = track_id

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

    def on_clear_selection(self):
        """Обработчик снятия выделения"""
        logger.debug("Снятие выделения")

        # Сбрасываем выбранный трек
        self.current_track_id = None

        # Показываем текущий экземпляр
        current_exemplar = self.simulator.get_current_exemplar()
        if current_exemplar and self.main_window:
            self.main_window.show_exemplar(current_exemplar)
            logger.debug("Показан текущий экземпляр")
        else:
            logger.warning("Нет текущего экземпляра для отображения")

    def _update_current_content(self):
        """Обновляет текущий контент для нового экземпляра"""
        current_exemplar = self.simulator.get_current_exemplar()
        if not current_exemplar:
            return

        # Если есть выбранный трек - обновляем его результат
        if self.current_track_id is not None:
            logger.debug(f"Обновляем трек {self.current_track_id} для нового экземпляра")
            result = self.simulator.run_track(current_exemplar, self.current_track_id)

            if isinstance(result, str):
                # Ошибка
                logger.error(f"Ошибка при обновлении трека {self.current_track_id}: {result}")
                if self.main_window:
                    self.main_window.show_empty(result)
            else:
                # Обновляем виджет трека
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

    def get_r_form(self):
        return self.simulator.rform

    def run(self):
        logger.info("Показываем окно симулятора")
        self.main_window = MainFormSimulator(r_form=self.get_r_form())
        self.main_window.show()
        self._init_first_exemplar()

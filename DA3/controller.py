import logging
from typing import Optional
from CORE.db_dataclasses import *
from DA3.model import Model
from DA3.main_form import MainForm
from DA3.start_dialog import select_form_from_dialog
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

from DA3.specialized_controllers import *

# Импортируем app_signals для типизации
import DA3.app_signals as app_signals


class Controller(QObject):
    def __init__(self, model: Model, main_window: MainForm):
        """
        Главный контроллер, координирующий работу специализированных контроллеров

        Args:
            model: Модель данных
            main_window: Главное окно приложения
        """
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.model = model
        self.main_window = main_window
        self.current_form: Optional[Form] = None

        # Инициализируем специализированные контроллеры
        self._init_specialized_controllers()

        # Инициализируем сигналы в контроллерах
        self._init_controller_signals()

    def _init_specialized_controllers(self):
        """Инициализация всех специализированных контроллеров"""
        # Создаем контроллеры, передавая себя в качестве родителя
        self.form_controller = FormController(self)
        self.point_controller = PointController(self)
        self.parameter_controller = ParameterController(self)
        self.pazzle_controller = PazzleController(self)
        self.step_controller = StepController(self)

        # Объединяем контроллеры для удобного доступа
        self.controllers = {
            'form': self.form_controller,
            'point': self.point_controller,
            'parameter': self.parameter_controller,
            'pazzle': self.pazzle_controller,
            'step': self.step_controller
        }

    def _init_controller_signals(self):
        """
        Явная инициализация сигналов в специализированных контроллерах.
        Здесь четко видно, какие группы сигналов передаются каждому контроллеру.
        """

        # Форма: передаем app_signals.form (объект класса AppSignals._Form)
        self.form_controller.init_signals(app_signals.form)

        # Точки: передаем app_signals.point (объект класса AppSignals._Point)
        self.point_controller.init_signals(app_signals.point)

        # Параметры: передаем app_signals.parameter (объект класса AppSignals._Parameter)
        self.parameter_controller.init_signals(app_signals.parameter)

        # Головоломки: передаем app_signals.base_pazzle (объект класса AppSignals._BasePazzle)
        self.pazzle_controller.init_signals(app_signals.base_pazzle)

        # Шаги: передаем app_signals.step (объект класса AppSignals._Step)
        self.step_controller.init_signals(app_signals.step)

        # Примечание: Сигналы треков (track) остаются нераспределенными
        # TODO: Создать TrackController и добавить его инициализацию здесь

        self.logger.info("Сигналы инициализированы в специализированных контроллерах")

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _refresh_form_data(self, form_id: int) -> None:
        """Загрузить актуальную форму из БД и обновить интерфейс"""
        try:
            updated_form = self.model.get_form_by_id(form_id)

            if updated_form:
                self.current_form = updated_form
                self.main_window.refresh(updated_form)
                self.logger.info(f"Форма ID:{form_id} обновлена в интерфейсе")
            else:
                self._show_error(f"Не удалось загрузить форму ID:{form_id} из базы данных")

        except Exception as e:
            error_msg = f"Ошибка при обновлении формы: {str(e)}"
            self.logger.error(error_msg)
            self._show_error(error_msg)

    def _show_success(self, message: str) -> None:
        """Показать сообщение об успехе"""
        QMessageBox.information(
            self.main_window,
            "Успешно",
            message,
            QMessageBox.StandardButton.Ok
        )
        self.logger.info(f"Успех: {message}")

    def _show_error(self, message: str) -> None:
        """Показать сообщение об ошибке"""
        QMessageBox.critical(
            self.main_window,
            "Ошибка",
            message,
            QMessageBox.StandardButton.Ok
        )
        self.logger.error(f"Ошибка: {message}")

    def refresh_form_data(self, form_id: int) -> None:
        """Обновить данные формы (публичный метод для доступа из специализированных контроллеров)"""
        self._refresh_form_data(form_id)

    # ==================== ИНИЦИАЛИЗАЦИЯ ФОРМЫ ====================

    def init_form_from_dialog(self) -> bool:
        """
        Инициализировать форму через диалог выбора

        Returns:
            True - форма успешно инициализирована
            False - пользователь отменил выбор или произошла ошибка
        """
        try:
            # Получаем список всех форм из базы данных
            forms = self.model.get_all_forms_summaries()
            self.logger.info(f"Загружено {len(forms)} форм из базы данных")

            # Показываем диалог выбора формы
            self.logger.info("Открытие диалога выбора формы...")
            form_id, create_new = select_form_from_dialog(forms)

            # Если пользователь закрыл диалог (не выбрал ничего и не создал новую)
            if form_id is None and not create_new:
                self.logger.info("Пользователь отменил выбор формы")
                return False

            # Определяем начальную форму
            if create_new:
                # Создаем новую пустую форму
                self.current_form = Form()
                self.logger.info("Пользователь выбрал создание новой формы")
            else:
                # Загружаем существующую форму по ID
                self.logger.info(f"Загрузка формы с ID={form_id}...")
                self.current_form = self.model.get_form_by_id(form_id)

                if self.current_form is None:
                    self.logger.error(f"Форма с ID={form_id} не найдена в базе данных")
                    return False

                self.logger.info(f"Загружена форма: '{self.current_form.name}' (ID: {self.current_form.id})")

            # Обновляем главное окно выбранной формой
            if self.current_form is not None:
                self.main_window.refresh(self.current_form)
                return True
            else:
                self.logger.error("Не удалось создать или загрузить форму")
                return False

        except Exception as e:
            self.logger.exception(f"Ошибка при инициализации формы: {e}")
            return False

    # ==================== ПУБЛИЧНЫЕ МЕТОДЫ ====================

    def get_controller(self, controller_type: str):
        """
        Получить специализированный контроллер по типу

        Args:
            controller_type: тип контроллера ('form', 'point', 'parameter', 'pazzle', 'step')

        Returns:
            Специализированный контроллер или None
        """
        return self.controllers.get(controller_type)
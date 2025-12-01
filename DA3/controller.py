import logging
from typing import Optional
from CORE.db_dataclasses import Form
from DA3.model import Model
from DA3.main_form import MainForm
from DA3.start_dialog import select_form_from_dialog
from DA3 import app_signals
from PySide6.QtCore import QObject


class Controller(QObject):
    def __init__(self, model: Model, main_window: MainForm):
        """
        Контроллер, связывающий модель и представление

        Args:
            model: Модель данных
            main_window: Главное окно приложения
        """
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.model = model
        self.main_window = main_window
        self.current_form: Optional[Form] = None

        # Инициализируем сигналы
        self._init_signals()

    def _init_signals(self):
        """Инициализация подключения сигналов"""
        # Подключаем сигнал запроса редактора основной информации
        app_signals.request_main_info_redactor.connect(self._open_main_info_redactor)

        self.logger.debug("Сигналы контроллера инициализированы")

    def _open_main_info_redactor(self, form: Form, parent_widget) -> None:
        """
        Открыть редактор основной информации о форме

        Args:
            form: Объект Form для редактирования
            parent_widget: Родительский виджет (для позиционирования диалога)
        """
        # Заглушка - просто логируем запрос
        self.logger.info(f"Запрос на редактирование основной информации формы ID={form.id}, имя='{form.name}'")
        self.logger.info(f"Родительский виджет: {parent_widget}")

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


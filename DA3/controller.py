import logging
from CORE.db_dataclasses import *
from DA3.model import Model
from DA3.main_form import MainForm
from DA3.start_dialog import select_form_from_dialog
from DA3 import app_signals
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox
from DA3.redactors_widgets import *
from DA3.form_widgets.dialog_new_step import AddStepDialog


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
        # Сигналы открытия редакторов
        app_signals.form.request_main_info_redactor.connect(self._open_main_info_redactor)
        app_signals.point.request_point_redactor.connect(self._open_point_redactor)
        app_signals.parameter.request_parameter_redactor.connect(self._open_parameter_redactor)
        app_signals.base_pazzle.request_hc_redactor.connect(self._open_hc_redactor)
        app_signals.base_pazzle.request_pc_redactor.connect(self._open_pc_redactor)
        app_signals.step.request_new_step_dialog.connect(self._open_step_add_gialog)
        app_signals.step.request_step_info_redactor.connect(self._open_step_info_redactor)

        # Сигналы добавления объектов (с обработкой результата)
        app_signals.form.db_add_form.connect(self._handle_add_form)
        app_signals.point.db_add_point.connect(self._handle_add_point)
        app_signals.parameter.db_add_parameter.connect(self._handle_add_parameter)
        app_signals.base_pazzle.db_add_hc.connect(self._handle_add_hc)
        app_signals.base_pazzle.db_add_pc.connect(self._handle_add_pc)
        app_signals.step.db_add_step.connect(self._handle_add_step)

        # Сигналы обновления объектов
        app_signals.db_actions.db_update_object.connect(self._handle_update_object)
        app_signals.form.db_update_form_main_info.connect(self._handle_update_form_main_info)

        # Сигналы удаления объектов
        app_signals.db_actions.db_delete_object.connect(self._handle_delete_object)

    # ==================== ОТКРЫТИЕ РЕДАКТОРОВ ====================

    @Slot(Parameter)
    def _open_parameter_redactor(self, parameter: Parameter) -> None:
        editor = ParameterEditor(self.main_window, parameter)
        editor.exec()

    @Slot(Step)
    def _open_step_add_gialog(self) -> None:
        dialog = AddStepDialog(parent=self.main_window, points=self.current_form.points)
        dialog.exec()

    @Slot(Step)
    def _open_step_info_redactor(self, step:Step)->None:
        editor = StepInfoEditor(parent=self.main_window,
                                points=self.current_form.points,
                                step=step)
        editor.exec()

    @Slot(Form)
    def _open_main_info_redactor(self, form: Form) -> None:
        """
        Открытие редактора основной информации формы

        Args:
            form: объект Form для редактирования
        """
        editor = FormEditor(self.main_window, form)
        editor.exec()

    @Slot(Point)
    def _open_point_redactor(self, point: Point) -> None:
        """
        Открытие редактора точки

        Args:
            point: объект Point для редактирования
        """
        editor = PointEditor(self.main_window, point)
        editor.exec()

    def _open_hc_redactor(self, hc:BasePazzle):
        classes_refs = self.model.get_HCs_classes()
        editor = HCEditor(self.main_window, form=self.current_form, hc=hc, classes_refs=classes_refs)
        editor.exec()

    def _open_pc_redactor(self, pc:BasePazzle):
        classes_refs = self.model.get_PCs_classes()
        editor = PCEditor(self.main_window, form=self.current_form, pc=pc, classes_refs=classes_refs)
        editor.exec()

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

    # ==================== ОБРАБОТЧИКИ ОПЕРАЦИЙ С БАЗОЙ ====================
    @Slot(Parameter)
    def _handle_add_parameter(self, parameter: Parameter) -> None:
        """Обработчик добавления параметра"""
        if self.current_form is None or self.current_form.id is None:
            self._show_error("Нет текущей формы для добавления параметра")
            return

        success, message = self.model.add_parameter(parameter, self.current_form.id)
        self._handle_db_result(success, message)

    @Slot(Form)
    def _handle_update_form_main_info(self, form: Form) -> None:
        """Обработчик обновления основной информации формы"""
        success, message = self.model.update_main_info(form)
        self._handle_db_result(success, message)

    @Slot(BasePazzle)
    def _handle_add_hc(self, hc:BasePazzle):
        """Обработчик добавления объекта типа HC"""
        success, message = self.model.add_HC(hc, form_id=self.current_form.id)
        self._handle_db_result( success, message)

    @Slot(BasePazzle)
    def _handle_add_pc(self, pc: BasePazzle):
        """Обработчик добавления объекта типа PC"""
        success, message = self.model.add_PC(pc, form_id=self.current_form.id)
        self._handle_db_result( success, message)

    @Slot(Form)
    def _handle_add_form(self, form: Form) -> None:
        """Обработчик добавления новой формы"""
        success, message = self.model.add_form(form)

        self._handle_db_result( success, message)

    @Slot(Point)
    def _handle_add_point(self, point: Point) -> None:
        """Обработчик добавления точки"""
        if self.current_form is None or self.current_form.id is None:
            self._show_error("Нет текущей формы для добавления точки")
            return

        success, message = self.model.add_point(point, self.current_form.id)

        self._handle_db_result( success, message)

    @Slot(Step)
    def _handle_add_step(self, step:Step) ->None:
        """Обработчик добавления шага"""
        if self.current_form is None or self.current_form.id is None:
            self._show_error("Нет текущей формы для добавления шага")
            return

        success, message = self.model.add_step(step, self.current_form.id)

        self._handle_db_result( success, message)

    @Slot(object)
    def _handle_update_object(self, obj) -> None:
        """Обработчик обновления любого объекта"""
        success, message = self.model.update_object(obj)

        self._handle_db_result( success, message)

    @Slot(object)
    def _handle_delete_object(self, obj) -> None:
        """Обработчик удаления объекта"""
        success, message = self.model.delete_object(obj)

        self._handle_db_result( success, message)

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


    def _handle_db_result(self, success, message):
        if success:
            self._refresh_form_data(self.current_form.id)
            self._show_success(message)
        else:
            self._show_error(message)





from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt, QTimer
from CORE.db_dataclasses import *


class BaseEditor(QDialog):
    """
    Базовый класс для всех модальных редакторов формы и ее компонентов.

    Основные функции:
    - Работа с глубокими копиями для изоляции изменений
    - Обработка внешних обновлений данных
    - Управление состоянием редактирования
    - Единый интерфейс для сохранения/отмены
    """

    def __init__(self, form: Form, controller):
        """
        Инициализация базового редактора.

        Args:
            form: Исходная форма для редактирования
            controller: Контроллер для доступа к сигналам и сервисам
        """
        super().__init__()
        self.controller = controller
        self.original_form = form  # Сохраняем ссылку на оригинальную форму
        self.modified_form = form.deep_copy()  # Работаем с глубокой копией!


        # Настройки окна
        self.setModal(True)  # Модальное окно - блокирует родительское
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowContextHelpButtonHint  # Убираем кнопку помощи
            | Qt.WindowCloseButtonHint  # Оставляем кнопку закрытия
        )


        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Базовая настройка UI - должна быть переопределена в потомках"""
        self.setMinimumSize(400, 300)
        self.layout = QVBoxLayout(self)

        # Статусная строка (общая для всех редакторов)
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: blue; padding: 5px;")
        self.status_label.setVisible(False)
        self.layout.addWidget(self.status_label)

    def _connect_signals(self):
        """
        Подключение сигналов контроллера.
        Обеспечивает реакцию на внешние изменения данных.
        """
        # Сигнал об обновлении формы извне (например, из другого редактора)
        self.controller.signals.form_updated.connect(self._refresh_editor_data)

        # Сигналы изменения данных в UI (для отслеживания несохраненных изменений)
        self._connect_data_change_signals()

    def _connect_data_change_signals(self):
        """
        Подключение сигналов изменения данных.
        Должен быть переопределен в потомках для отслеживания изменений в полях ввода.
        """
        pass


    def _refresh_editor_data(self, updated_form: Form):
        """
        Обновляет данные в редакторе при внешнем изменении формы.
        Вызывается только если нет конфликтов данных.

        Args:
            updated_form: Обновленная форма для синхронизации
        """
        raise NotImplementedError("Метод должен быть реализован в потомке")


    def _add_action_buttons(self, layout):
        """
        Добавляет стандартные кнопки действий в layout.

        Args:
            layout: Layout для добавления кнопок
        """
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")

        # Настройка кнопок
        self.save_button.setDefault(True)  # Кнопка по умолчанию (работает по Enter)
        self.save_button.setMinimumWidth(100)
        self.cancel_button.setMinimumWidth(100)

        # Подключение сигналов
        self.save_button.clicked.connect(self._on_save_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _on_save_clicked(self):
        """Обработчик клика по кнопке Сохранить"""
        if self._validate_data():
            self.accept()  # Закрывает диалог с результатом QDialog.Accepted
        else:
            # Данные не прошли валидацию - остаемся в редакторе
            pass

    def _on_cancel_clicked(self):
        """Обработчик клика по кнопке Отмена"""
        self.reject()

    def _validate_data(self) -> bool:
        """
        Валидация введенных данных.

        Returns:
            bool: True если данные корректны
        """
        # Базовая реализация - данные всегда валидны
        # Потомки должны переопределить для конкретной логики валидации
        return True

    def get_modified_form(self) -> Form:
        """
        Возвращает модифицированную форму для сохранения.

        Returns:
            Form: Глубокая копия формы с внесенными изменениями
        """
        # Потомки должны обновить modified_form перед возвратом
        return self.modified_form

    def closeEvent(self, event):
        """
        Обработчик закрытия окна (крестик или Alt+F4).
        Обеспечивает корректное отключение сигналов.
        """
        self._disconnect_signals()
        super().closeEvent(event)

    def _disconnect_signals(self):
        """Корректное отключение сигналов при закрытии редактора"""
        try:
            self.controller.signals.form_updated.disconnect(self._refresh_editor_data)
        except (TypeError, RuntimeError):
            # Сигналы уже отключены или объект удален
            pass


    def exec(self) -> bool:
        """
        Запуск модального диалога.

        Returns:
            bool: True если пользователь нажал Сохранить, False если Отмена
        """
        result = super().exec()
        return result == QDialog.Accepted
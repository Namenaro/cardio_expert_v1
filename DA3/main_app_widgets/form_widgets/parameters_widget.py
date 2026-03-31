from typing import List

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QMessageBox, QScrollArea, QSizePolicy
)

from CORE.db_dataclasses import Parameter
from DA3 import app_signals
from DA3.base_widget import BaseWidget


class ParametersWidget(BaseWidget):
    """Виджет для работы с параметрами формы"""

    def __init__(self):
        super().__init__()
        self._parameters: List[Parameter] = []
        self.setup_ui()
        self.apply_styles("common.qss", "parameters_widget.qss")

    def setup_ui(self):
        # Основной layout - уменьшенные отступы
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Заголовок
        title_label = QLabel("Параметры формы")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("mainTitle")
        main_layout.addWidget(title_label)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none;")

        # Контейнер для списка параметров
        self.parameters_container = QWidget()
        self.parameters_container.setObjectName("parametersContainer")
        self.parameters_layout = QVBoxLayout(self.parameters_container)
        self.parameters_layout.setSpacing(4)
        self.parameters_layout.setContentsMargins(4, 4, 4, 4)
        self.parameters_layout.addStretch()

        scroll_area.setWidget(self.parameters_container)
        main_layout.addWidget(scroll_area)

        # Кнопка добавления
        self.add_button = QPushButton("Добавить параметр")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.on_add_parameter_clicked)
        self.add_button.setMinimumHeight(32)

        main_layout.addWidget(self.add_button)

    def reset_parameters(self, parameters: List[Parameter]) -> None:
        """Установить новый список параметров"""
        self._parameters = parameters
        self.refresh()

    def refresh(self) -> None:
        """Обновить отображение списка параметров"""
        # Очищаем текущий список
        while self.parameters_layout.count() > 1:
            item = self.parameters_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Добавляем виджеты для каждого параметра
        for parameter in self._parameters:
            self._add_parameter_widget(parameter)

    def _add_parameter_widget(self, parameter: Parameter) -> None:
        """Создать и добавить виджет для одного параметра"""
        # Фрейм для параметра
        parameter_frame = QFrame()
        parameter_frame.setObjectName("parameterFrame")
        parameter_frame.setFrameShape(QFrame.Shape.NoFrame)
        parameter_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Layout для фрейма - уменьшенные отступы
        frame_layout = QVBoxLayout(parameter_frame)
        frame_layout.setContentsMargins(10, 8, 10, 8)
        frame_layout.setSpacing(4)

        # === ВЕРХНЯЯ ЧАСТЬ: ID и кнопки ===
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        # ID параметра
        id_text = f"ID{parameter.id if parameter.id is not None else '?'}"
        id_label = QLabel(id_text)
        id_label.setObjectName("idLabel")
        top_layout.addWidget(id_label)

        top_layout.addStretch()

        # Кнопка редактирования
        edit_button = QPushButton("Редактировать")
        edit_button.setObjectName("editParameterButton")
        edit_button.clicked.connect(lambda checked, p=parameter: self.on_edit_parameter_clicked(p))
        top_layout.addWidget(edit_button)

        # Кнопка удаления
        delete_button = QPushButton("Удалить")
        delete_button.setObjectName("deleteParameterButton")
        delete_button.clicked.connect(lambda checked, p=parameter: self.on_delete_parameter_clicked(p))
        top_layout.addWidget(delete_button)

        frame_layout.addLayout(top_layout)

        # === НАЗВАНИЕ ПАРАМЕТРА ===
        name_text = parameter.name if parameter.name else "<Название не указано>"
        name_label = QLabel(name_text)
        name_label.setObjectName("nameLabel")
        name_label.setWordWrap(True)
        frame_layout.addWidget(name_label)

        # === КОММЕНТАРИЙ (если есть) ===
        if parameter.comment:
            comment_label = QLabel(parameter.comment)
            comment_label.setObjectName("commentLabel")
            comment_label.setWordWrap(True)
            frame_layout.addWidget(comment_label)

        # Добавляем фрейм
        self.parameters_layout.insertWidget(self.parameters_layout.count() - 1, parameter_frame)

    @Slot(Parameter)
    def on_edit_parameter_clicked(self, parameter: Parameter) -> None:
        """Обработчик нажатия кнопки редактирования параметра"""
        app_signals.parameter.request_parameter_redactor.emit(parameter)

    @Slot(Parameter)
    def on_delete_parameter_clicked(self, parameter: Parameter) -> None:
        """Обработчик нажатия кнопки удаления параметра"""
        if parameter.id is None:
            QMessageBox.warning(self, "Ошибка", "Параметр не сохранен в базе данных")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить параметр '{parameter.name if parameter.name else 'без названия'}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            app_signals.parameter.db_delete_parameter.emit(parameter)

    @Slot()
    def on_add_parameter_clicked(self) -> None:
        """Обработчик нажатия кнопки добавления нового параметра"""
        new_parameter = Parameter()
        app_signals.parameter.request_parameter_redactor.emit(new_parameter)
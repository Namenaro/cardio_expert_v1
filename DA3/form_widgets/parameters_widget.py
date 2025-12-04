from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QMessageBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from CORE.db_dataclasses import Parameter
from DA3 import app_signals


class ParametersWidget(QWidget):
    """Виджет для работы с параметрами формы"""

    def __init__(self):
        super().__init__()
        self._parameters: List[Parameter] = []
        self.setup_ui()

    def setup_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel("Параметры формы")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Область прокрутки для списка параметров
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Контейнер для списка параметров
        self.parameters_container = QWidget()
        self.parameters_layout = QVBoxLayout(self.parameters_container)
        self.parameters_layout.setSpacing(5)
        self.parameters_layout.setContentsMargins(5, 5, 5, 5)
        self.parameters_layout.addStretch()

        scroll_area.setWidget(self.parameters_container)
        main_layout.addWidget(scroll_area)

        # Кнопка добавления нового параметра
        self.add_button = QPushButton("Добавить параметр")
        self.add_button.clicked.connect(self.on_add_parameter_clicked)
        self.add_button.setMinimumHeight(40)
        main_layout.addWidget(self.add_button)

        self.setStyleSheet("background-color: #ffe6e6;")  # Другой цвет для отличия

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
        parameter_frame.setFrameShape(QFrame.Shape.Box)
        parameter_frame.setLineWidth(1)
        parameter_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        parameter_frame.setMinimumHeight(70)  # Минимальная высота для отображения всей информации

        # Layout для фрейма
        frame_layout = QVBoxLayout(parameter_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)

        # === ВЕРХНЯЯ ЧАСТЬ: ID и кнопки ===
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 5)

        # ID параметра (нередактируемый)
        id_label = QLabel(f"ID{parameter.id if parameter.id is not None else '?'}")
        id_label.setFont(QFont("Arial", 8))
        id_label.setStyleSheet("color: #666666; font-style: italic;")
        top_layout.addWidget(id_label)

        # Пустое пространство
        top_layout.addStretch()

        # Кнопка редактирования
        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(lambda checked, p=parameter: self.on_edit_parameter_clicked(p))
        top_layout.addWidget(edit_button)

        # Кнопка удаления
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(lambda checked, p=parameter: self.on_delete_parameter_clicked(p))
        top_layout.addWidget(delete_button)

        frame_layout.addLayout(top_layout)

        # === СРЕДНЯЯ ЧАСТЬ: Название параметра ===
        name_label = QLabel(parameter.name if parameter.name else "<Название не указано>")
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        name_label.setWordWrap(True)
        frame_layout.addWidget(name_label)

        # === НИЖНЯЯ ЧАСТЬ: Комментарий ===
        if parameter.comment:
            comment_label = QLabel(parameter.comment)
            comment_label.setFont(QFont("Arial", 9))
            comment_label.setStyleSheet("color: #444444; font-style: italic;")
            comment_label.setWordWrap(True)
            comment_label.setMaximumHeight(40)  # Ограничиваем высоту комментария
            frame_layout.addWidget(comment_label)

        # Добавляем фрейм
        self.parameters_layout.insertWidget(self.parameters_layout.count() - 1, parameter_frame)

    @Slot(Parameter)
    def on_edit_parameter_clicked(self, parameter: Parameter) -> None:
        """Обработчик нажатия кнопки редактирования параметра"""
        app_signals.request_parameter_redactor.emit(parameter)

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
            # Испускаем сигнал с объектом Parameter
            app_signals.db_delete_object.emit(parameter)

    @Slot()
    def on_add_parameter_clicked(self) -> None:
        """Обработчик нажатия кнопки добавления нового параметра"""
        # Создаем новый параметр и отправляем в редактор
        new_parameter = Parameter()
        app_signals.request_parameter_redactor.emit(new_parameter)
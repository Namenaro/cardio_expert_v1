from typing import Optional, List
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from DA3 import app_signals
from CORE.db_dataclasses import BasePazzle, Parameter, ObjectInputParamValue


class HCCard(QFrame):
    """Карточка для отображения HC объекта"""

    def __init__(self, hc: BasePazzle, form_parameters: List[Parameter], parent=None):
        """
        Инициализация карточки

        Args:
            hc: HC объект
            form_parameters: Список параметров формы
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.hc = hc
        self.form_parameters = form_parameters  # Параметры формы для поиска имен
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса карточки"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(2)
        self.setFixedWidth(220)  # Увеличили ширину для параметров
        self.setMinimumHeight(180)  # Увеличили высоту

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Заголовок с ID
        title_label = QLabel(f"ID: {self.hc.id if self.hc.id else 'Новый'}")
        layout.addWidget(title_label)

        # Имя
        name_label = QLabel(f"Имя: {self.hc.name if self.hc.name else 'Без имени'}")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Имя класса (если есть)
        if self.hc.class_ref and hasattr(self.hc.class_ref, 'name') and self.hc.class_ref.name:
            class_label = QLabel(f"Класс: {self.hc.class_ref.name}")
            class_label.setStyleSheet("color: #2c5282;")
            class_label.setWordWrap(True)
            layout.addWidget(class_label)
        elif self.hc.class_ref and hasattr(self.hc.class_ref, 'id') and self.hc.class_ref.id:
            # Если есть только ID класса
            class_label = QLabel(f"Класс ID: {self.hc.class_ref.id}")
            class_label.setStyleSheet("color: #718096; font-style: italic;")
            layout.addWidget(class_label)

        # Затронутые параметры формы
        affected_params = self._get_affected_form_parameters()
        if affected_params:
            params_label = QLabel(f"Параметры: {affected_params}")
            params_label.setStyleSheet("color: #2d3748; font-size: 15px;")
            params_label.setWordWrap(True)
            params_label.setMaximumHeight(30)
            params_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout.addWidget(params_label)

        # Комментарий
        if self.hc.comment:
            comment_text = f"Комментарий: {self.hc.comment}"
            comment_label = QLabel(comment_text)
            comment_label.setWordWrap(True)
            comment_label.setMaximumHeight(30)
            comment_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            comment_label.setStyleSheet("color: #4a5568; font-size: 15px;")
            layout.addWidget(comment_label)

        layout.addStretch()

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.on_edit_clicked)
        edit_btn.setFixedHeight(25)
        edit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.on_delete_clicked)
        delete_btn.setFixedHeight(25)
        delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        delete_btn.setStyleSheet("color: #c53030;")
        buttons_layout.addWidget(delete_btn)

        layout.addLayout(buttons_layout)

    def _get_affected_form_parameters(self) -> str:
        """
        Получить строку с названиями затронутых параметров формы

        Returns:
            Строка с названиями параметров через запятую или пустая строка
        """
        if not hasattr(self.hc, 'input_param_values') or not self.hc.input_param_values:
            return ""

        # Собираем ID параметров формы из input_param_values
        param_ids = []
        for param_value in self.hc.input_param_values:
            if (isinstance(param_value, ObjectInputParamValue) and
                    hasattr(param_value, 'parameter_id') and
                    param_value.parameter_id is not None):
                param_ids.append(param_value.parameter_id)

        if not param_ids:
            return ""

        # Ищем имена параметров в списке form_parameters
        param_names = []
        for param_id in param_ids:
            # Ищем параметр по ID
            found_param = None
            for param in self.form_parameters:
                if param.id == param_id:
                    found_param = param
                    break

            if found_param and found_param.name:
                param_names.append(found_param.name)
            else:
                param_names.append(f"ID:{param_id}")

        # Объединяем и ограничиваем длину
        result = ", ".join(param_names)
        if len(result) > 40:  # Ограничиваем длину для компактности
            result = result[:37] + "..."

        return result

    def on_edit_clicked(self):
        """Обработчик нажатия кнопки редактирования"""
        app_signals.request_hc_redactor.emit(self.hc)

    def on_delete_clicked(self):
        """Обработчик нажатия кнопки удаления"""
        hc_name = self.hc.name if self.hc.name else "без имени"
        hc_id = self.hc.id if self.hc.id else "новый"

        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы точно хотите удалить жесткое условие "{hc_name}" (ID: {hc_id})?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            app_signals.db_delete_object.emit(self.hc)
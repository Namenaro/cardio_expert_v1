from typing import Optional, List
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QMessageBox, QSizePolicy, QScrollArea, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from DA3 import app_signals
from CORE.db_dataclasses import BasePazzle, Parameter, ObjectInputParamValue
from DA3.utils.utils import get_affected_form_parameters
from DA3.utils.style_loader import get_style_loader


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
        self.apply_styles()

    def setup_ui(self):
        """Настройка интерфейса карточки"""
        self.setFixedWidth(240)
        self.setMinimumHeight(180)
        self.setMaximumHeight(220)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Заголовок с ID
        title_label = QLabel(f"ID: {self.hc.id if self.hc.id else 'Новый'}")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        # Создаем контейнер для всего содержимого
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Имя
        name_label = QLabel(f"Имя: {self.hc.name if self.hc.name else 'Без имени'}")
        name_label.setObjectName("nameLabel")
        name_label.setWordWrap(True)
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        content_layout.addWidget(name_label)

        # Добавляем отступ между полями
        content_layout.addSpacing(4)

        # Имя класса (если есть)
        if self.hc.class_ref and hasattr(self.hc.class_ref, 'name') and self.hc.class_ref.name:
            class_label = QLabel(f"Класс: {self.hc.class_ref.name}")
            class_label.setObjectName("classLabel")
            class_label.setWordWrap(True)
            class_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            content_layout.addWidget(class_label)
            content_layout.addSpacing(4)
        elif self.hc.class_ref and hasattr(self.hc.class_ref, 'id') and self.hc.class_ref.id:
            class_label = QLabel(f"Класс ID: {self.hc.class_ref.id}")
            class_label.setObjectName("classIdLabel")
            class_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            content_layout.addWidget(class_label)
            content_layout.addSpacing(4)

        # Затронутые параметры формы
        affected_params_names = get_affected_form_parameters(puzzle=self.hc,
                                                             form_parameters=self.form_parameters)
        affected_params_result = ", ".join(affected_params_names)

        if affected_params_result:
            params_label = QLabel(f"Параметры: {affected_params_result}")
            params_label.setObjectName("paramsLabel")
            params_label.setWordWrap(True)
            params_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            content_layout.addWidget(params_label)
            content_layout.addSpacing(4)

        # Комментарий
        if self.hc.comment:
            comment_text = f"{self.hc.comment}"
            comment_label = QLabel(comment_text)
            comment_label.setObjectName("commentLabel")
            comment_label.setWordWrap(True)
            comment_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            content_layout.addWidget(comment_label)

        # Добавляем растяжку в контейнере, чтобы прижать содержимое к верху
        content_layout.addStretch()

        # Оборачиваем контейнер в скролл-область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(content_container)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        main_layout.addWidget(scroll_area)

        # Добавляем растяжку после скролл-области, чтобы кнопки прижались вниз
        main_layout.addStretch()

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.on_edit_clicked)
        edit_btn.setFixedHeight(25)
        edit_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.setObjectName("deleteButton")
        delete_btn.clicked.connect(self.on_delete_clicked)
        delete_btn.setFixedHeight(25)
        delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        buttons_layout.addWidget(delete_btn)

        main_layout.addLayout(buttons_layout)

    def apply_styles(self):
        """Применяет стили к карточке"""
        style_loader = get_style_loader()
        style_loader.apply_style(self, "hc_card.qss")

    def on_edit_clicked(self):
        """Обработчик нажатия кнопки редактирования"""
        app_signals.base_pazzle.request_hc_redactor.emit(self.hc)

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
            app_signals.base_pazzle.db_delete_pazzle.emit(self.hc)
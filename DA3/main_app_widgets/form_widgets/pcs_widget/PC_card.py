from typing import List

from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QMessageBox, QSizePolicy, QScrollArea, QWidget)
from PySide6.QtCore import Qt

from CORE.db_dataclasses import BasePazzle, Parameter, Point
from DA3 import app_signals
from DA3.utils.style_loader import get_style_loader


class PCCard(QFrame):
    """Карточка для отображения PC объекта"""

    def __init__(self, pc: BasePazzle, form_parameters: List[Parameter], form_points: List[Point], parent=None):

        super().__init__(parent)
        self.pc = pc
        self.form_parameters = form_parameters  # Параметры формы для поиска имен
        self.form_points = form_points

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.setFixedWidth(220)
        self.setMinimumHeight(180)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравнивание всего лейаута вверх

        # Заголовок с ID
        title_label = QLabel(f"ID: {self.pc.id if self.pc.id else 'Новый'}")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        # Создаем контейнер для имени и комментария
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравнивание содержимого вверх

        # Имя
        name_label = QLabel(f"Имя: {self.pc.name if self.pc.name else 'Без имени'}")
        name_label.setObjectName("nameLabel")
        name_label.setWordWrap(True)
        name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        info_layout.addWidget(name_label)

        # Добавляем фиксированный отступ между именем и комментарием
        info_layout.addSpacing(8)

        # Комментарий
        if self.pc.comment:
            comment_text = f"{self.pc.comment}"
            comment_label = QLabel(comment_text)
            comment_label.setObjectName("commentLabel")
            comment_label.setWordWrap(True)
            comment_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            info_layout.addWidget(comment_label)

        # Добавляем растяжку в контейнере, чтобы прижать содержимое к верху,
        # но если контент маленький, то он останется вверху
        info_layout.addStretch()

        # Оборачиваем контейнер в скролл-область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(info_container)

        # Устанавливаем политику размера, чтобы скролл-область не растягивалась
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Добавляем скролл-область в основной лейаут
        main_layout.addWidget(scroll_area)

        # Добавляем растяжку после скролл-области, чтобы кнопки прижались вниз,
        # но сам контент оставался вверху
        main_layout.addStretch()

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Кнопки выравниваем вниз

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
        style_loader.apply_style(self, "pc_card.qss")

    def on_edit_clicked(self):
        """Обработчик нажатия кнопки редактирования"""
        app_signals.base_pazzle.request_pc_redactor.emit(self.pc)

    def on_delete_clicked(self):
        """Обработчик нажатия кнопки удаления"""
        hc_name = self.pc.name if self.pc.name else "без имени"
        hc_id = self.pc.id if self.pc.id else "новый"

        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы точно хотите удалить расчетчик параметров "{hc_name}" (ID: {hc_id})?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            app_signals.base_pazzle.db_delete_pazzle.emit(self.pc)
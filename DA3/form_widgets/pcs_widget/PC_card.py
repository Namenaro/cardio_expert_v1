from typing import Optional, List
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from DA3 import app_signals
from CORE.db_dataclasses import BasePazzle, Parameter, Point, ObjectInputParamValue


class PCCard(QFrame):
    """Карточка для отображения PC объекта"""

    def __init__(self, pc: BasePazzle, form_parameters: List[Parameter], form_points: List[Point],parent=None):

        super().__init__(parent)
        self.pc = pc
        self.form_parameters = form_parameters  # Параметры формы для поиска имен
        self.form_points = form_points

        self.setup_ui()


    def setup_ui(self):
        self.setFixedWidth(220)
        self.setMinimumHeight(180)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Заголовок с ID
        title_label = QLabel(f"ID: {self.pc.id if self.pc.id else 'Новый'}")
        layout.addWidget(title_label)

        # Имя
        name_label = QLabel(f"Имя: {self.pc.name if self.pc.name else 'Без имени'}")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Комментарий
        if self.pc.comment:
            comment_text = f"Комментарий: {self.pc.comment}"
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






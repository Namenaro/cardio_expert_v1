from typing import Optional, List
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QLabel, QMessageBox, QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from DA3 import app_signals
from CORE.db_dataclasses import BasePazzle, Form


class HCCard(QFrame):
    """Карточка для отображения HC объекта"""

    def __init__(self, hc: BasePazzle, parent=None):
        super().__init__(parent)
        self.hc = hc
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса карточки"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(2)
        self.setFixedWidth(200)
        self.setMinimumHeight(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Заголовок с ID
        title_label = QLabel(f"ID: {self.hc.id if self.hc.id else 'Новый'}")
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Имя
        name_label = QLabel(f"Имя: {self.hc.name if self.hc.name else 'Без имени'}")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Комментарий
        comment_label = QLabel(f"Комментарий: {self.hc.comment if self.hc.comment else 'Нет комментария'}")
        comment_label.setWordWrap(True)
        comment_label.setMaximumHeight(50)
        comment_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(comment_label)

        # Кнопки действий
        buttons_layout = QHBoxLayout()

        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self.on_edit_clicked)
        edit_btn.setFixedHeight(30)
        buttons_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.on_delete_clicked)
        delete_btn.setFixedHeight(30)
        buttons_layout.addWidget(delete_btn)

        layout.addLayout(buttons_layout)

    def on_edit_clicked(self):
        """Обработчик нажатия кнопки редактирования"""
        app_signals.request_hc_redactor.emit(self.hc)

    def on_delete_clicked(self):
        """Обработчик нажатия кнопки удаления"""
        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы точно хотите удалить HC объект "{self.hc.name if self.hc.name else "без имени"}" (ID: {self.hc.id if self.hc.id else "новый"})?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            app_signals.db_delete_object.emit(self.hc)
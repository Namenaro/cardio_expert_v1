from typing import Optional, List
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QLabel, QMessageBox, QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal

from DA3 import app_signals
from CORE.db_dataclasses import BasePazzle, Form, Parameter
from DA3.form_widgets.hcs_widget.HC_card import HCCard


class HCsWidget(QWidget):
    """Виджет для отображения HC объектов формы"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._form: Optional[Form] = None
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса виджета"""
        # Основной вертикальный layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Заголовок
        title_label = QLabel("Жесткие условия на параметры")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333;
                padding: 5px 15px;
                background-color: #f5f5f5;
            }
        """)
        title_label.setFixedHeight(30)
        main_layout.addWidget(title_label)

        # Горизонтальный layout для содержимого
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        # Левая панель с кнопкой добавления
        left_panel = QWidget()
        left_panel.setFixedWidth(60)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(50, 50)
        add_btn.setToolTip("Добавить новый HC объект")
        add_btn.clicked.connect(self.on_add_clicked)

        left_layout.addWidget(add_btn)
        left_layout.addStretch()

        content_layout.addWidget(left_panel)

        # Область с карточками
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background-color: #f5f5f5;")
        self.cards_layout = QHBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        scroll_area.setWidget(self.cards_widget)
        content_layout.addWidget(scroll_area)

        main_layout.addWidget(content_widget)

    def on_add_clicked(self):
        """Обработчик нажатия кнопки добавления"""
        if self._form is None:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Форма не установлена. Сначала установите форму."
            )
            return

        # Создаем пустой объект BasePazzle
        hc = BasePazzle()

        # Испускаем сигнал с пустым объектом
        app_signals.base_pazzle.request_hc_redactor.emit(hc)

    def reset_form(self, form: Form) -> None:
        """Установить новую форму"""
        self._form = form
        self.refresh()

    def refresh(self):
        """Обновить отображение карточек"""
        # Очищаем старые карточки
        self.clear_cards()

        if self._form is None:
            return

        # Добавляем карточки только для HC объектов
        for hc_object in self._form.HC_PC_objects:
            if hc_object.is_HC():
                # Создаем карточку с передачей параметров формы
                card = HCCard(hc_object, self._form.parameters, self)
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def clear_cards(self):
        """Очистить все карточки"""
        # Удаляем все виджеты кроме stretch
        while self.cards_layout.count() > 1:  # Оставляем stretch
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()



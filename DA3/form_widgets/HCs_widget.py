from typing import Optional, List
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QLabel, QMessageBox, QScrollArea, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from DA3 import app_signals
from CORE.db_dataclasses import BasePazzle, Form


class PCCard(QFrame):
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


class HCsWidget(QWidget):
    """Виджет для отображения HC объектов формы"""

    # Сигналы
    hc_added = Signal(BasePazzle, Form)  # Альтернативный сигнал, если нужно

    def __init__(self, parent=None):
        super().__init__(parent)
        self._form: Optional[Form] = None
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса виджета"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

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

        main_layout.addWidget(left_panel)

        # Область с карточками
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cards_widget = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        scroll_area.setWidget(self.cards_widget)
        main_layout.addWidget(scroll_area)

        self.setStyleSheet("background-color: lightyellow;")

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
        app_signals.request_hc_redactor.emit(hc)

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
                card = PCCard(hc_object, self)
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def clear_cards(self):
        """Очистить все карточки"""
        # Удаляем все виджеты кроме stretch
        while self.cards_layout.count() > 1:  # Оставляем stretch
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Убедимся, что stretch есть в конце
        if self.cards_layout.count() == 0:
            self.cards_layout.addStretch()
        elif not isinstance(self.cards_layout.itemAt(0), QWidget):
            # Если первый элемент не виджет, значит это stretch
            pass
        else:
            self.cards_layout.addStretch()

    def add_hc_object(self, hc: BasePazzle):
        """Добавить HC объект вручную (если требуется)"""
        if self._form and hasattr(self._form, 'HC_PC_objects'):
            self._form.HC_PC_objects.append(hc)
            self.refresh()

    def remove_hc_object(self, hc: BasePazzle):
        """Удалить HC объект (если требуется)"""
        if self._form and hasattr(self._form, 'HC_PC_objects'):
            if hc in self._form.HC_PC_objects:
                self._form.HC_PC_objects.remove(hc)
                self.refresh()

    def get_form(self) -> Optional[Form]:
        """Получить текущую форму"""
        return self._form
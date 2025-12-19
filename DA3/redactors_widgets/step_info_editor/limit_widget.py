from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QRadioButton, QGroupBox
)
from DA3.redactors_widgets.base_editor import BaseEditor
from DA3 import app_signals
from CORE.db_dataclasses import *
from copy import deepcopy




class LimitWidget(QGroupBox):
    """Виджет для выбора ограничения: либо точка, либо отступ (t)"""

    def __init__(self, parent: QWidget, points: List[Point], title: str):
        super().__init__(parent)
        self.setTitle(title)

        # Сохраняем points как атрибут экземпляра
        self._points = points

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Радио-кнопки
        self.point_radio = QRadioButton("Имя точки")
        self.padding_radio = QRadioButton("Отступ (t)")
        layout.addWidget(self.point_radio)
        layout.addWidget(self.padding_radio)

        # Блок выбора точки
        hlayout_point = QHBoxLayout()
        hlayout_point.addWidget(QLabel("Точка:"))
        self.point_combo = QComboBox()
        self._fill_combo_with_points(self.point_combo)
        hlayout_point.addWidget(self.point_combo)
        layout.addLayout(hlayout_point)


        # Блок ввода отступа
        hlayout_padding = QHBoxLayout()
        hlayout_padding.addWidget(QLabel("Отступ (t):"))
        self.padding_edit = QLineEdit()
        self.padding_edit.setPlaceholderText("0.0")
        hlayout_padding.addWidget(self.padding_edit)
        layout.addLayout(hlayout_padding)

        # Логика переключения
        self.point_radio.toggled.connect(self._on_toggled)
        self.padding_radio.toggled.connect(self._on_toggled)

    def _fill_combo_with_points(self, combo: QComboBox):
        """Заполняет комбобокс точками"""
        combo.addItem("—", None)
        for point in self._points:  # Теперь self._points существует!
            combo.addItem(point.name, point)


    def _on_toggled(self, checked: bool):
        """Обработчик переключения радио-кнопок"""
        sender = self.sender()
        if sender is self.point_radio and checked:
            self.point_combo.setEnabled(True)
            self.padding_edit.setEnabled(False)
            self.padding_edit.setText("")
        elif sender is self.padding_radio and checked:
            self.point_combo.setCurrentIndex(0)
            self.point_combo.setEnabled(False)
            self.padding_edit.setEnabled(True)


    def set_value(self, point: Point = None, padding: float = None):
        """Устанавливает текущее значение виджета"""
        if point is not None:
            self.point_radio.setChecked(True)
            idx = self.point_combo.findData(point)
            if idx != -1:
                self.point_combo.setCurrentIndex(idx)
        elif padding is not None:
            self.padding_radio.setChecked(True)
            self.padding_edit.setText(str(padding))
        else:
            self.point_radio.setChecked(True)
            self.point_combo.setCurrentIndex(0)


    def get_value(self) -> tuple[Point | None, float | None]:
        """Возвращает (точка, отступ) — только одно из двух будет не-None"""
        if self.point_radio.isChecked():
            return self.point_combo.currentData(), None
        elif self.padding_radio.isChecked():
            try:
                return None, float(self.padding_edit.text())
            except ValueError:
                return None, None
        else:
            return None, None  # на случай, если ни одна кнопка не выбрана
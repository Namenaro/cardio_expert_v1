from typing import List, Optional
from PySide6.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QPushButton, QApplication
)
from PySide6.QtCore import Qt

from DA3.form_widgets.steps_widget.step_card import StepCard
from CORE.db_dataclasses import Step
from DA3 import app_signals
from DA3.base_widget import BaseWidget


class StepsWidget(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._steps: Optional[List[Step]] = None
        self.setup_ui()
        self.apply_styles("common.qss", "steps_widget.qss")

    def setup_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setMovable(False)
        self.tab_widget.setDocumentMode(False)

        main_layout.addWidget(self.tab_widget, 1)

        # Кнопка добавления шага
        self.btn_add_step = QPushButton("+ Добавить шаг")
        self.btn_add_step.setObjectName("addStepButton")
        self.btn_add_step.clicked.connect(self.on_add_step_clicked)

        main_layout.addWidget(self.btn_add_step)

    def reset_steps(self, steps: List[Step]) -> None:
        """Установить новый список шагов"""
        self._steps = steps
        self.refresh()

    def refresh(self) -> None:
        """Обновить отображение списка шагов"""
        # Сохраняем индекс текущей выбранной вкладки
        current_index = self.tab_widget.currentIndex()

        # Удаляем все вкладки
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)

        if not self._steps:
            return

        # Сортируем шаги по номеру
        sorted_steps = sorted(self._steps, key=lambda s: s.num_in_form)

        for step in sorted_steps:
            target_point_name = step.target_point.name if step.target_point else "Не задано"
            tab_title = f"{step.num_in_form}. {target_point_name}"
            step_card = StepCard(step)
            self.tab_widget.addTab(step_card, tab_title)

        # Восстанавливаем выбранную вкладку, если индекс валиден
        if 0 <= current_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(current_index)

    def on_add_step_clicked(self):
        """Обработчик нажатия кнопки добавления шага"""
        app_signals.step.request_new_step_dialog.emit()
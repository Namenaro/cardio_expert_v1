from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QFrame
)

from CORE.run.r_form import RForm
from CORE.run.r_ps import R_PS
from CORE.run.r_sm import R_SM
from CORE.run.r_step import RStep
from CORE.run.r_track import RTrack
from DA3.base_widget import BaseWidget
from DA3.simulation_app.simulator_signals import get_signals


class IdSelector(BaseWidget):
    """Виджет для отображения и выбора шагов, треков, SM и PS"""

    def __init__(self, r_form: RForm, parent=None):
        super().__init__(parent)
        self.r_form = r_form
        self.rsteps: List[RStep] = r_form.rsteps

        # Для хранения текущего выбранного виджета
        self.current_selected: Optional[QPushButton] = None

        # Получаем сигналы
        self.signals = get_signals()

        self._setup_ui()
        self._build_structure()

        # Применяем стили только из id_selector.qss
        self.apply_styles("id_selector.qss")

    def _setup_ui(self):
        """Настройка UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        # Создаем скролл-область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Основной контейнер
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(8)

        scroll_area.setWidget(self.main_widget)
        layout.addWidget(scroll_area)

    def _build_structure(self):
        """Построение структуры из шагов, треков, SM и PS"""
        self._clear_layout(self.main_layout)
        self.current_selected = None

        for step in self.rsteps:
            self._add_step_widget(step)

    def _clear_selection(self):
        """Снимает выделение с текущего выбранного виджета"""
        if self.current_selected:
            self.current_selected.setProperty("selected", False)
            self.current_selected.style().unpolish(self.current_selected)
            self.current_selected.style().polish(self.current_selected)
            self.current_selected = None

    def _set_selected(self, button: QPushButton):
        """Устанавливает выделение на виджет"""
        self._clear_selection()
        self.current_selected = button
        self.current_selected.setProperty("selected", True)
        self.current_selected.style().unpolish(self.current_selected)
        self.current_selected.style().polish(self.current_selected)

    def _add_step_widget(self, step: RStep):
        """Добавляет виджет для шага"""
        step_container = QFrame()
        step_container.setProperty("class", "step-container")
        step_container.setFrameShape(QFrame.Shape.StyledPanel)

        step_layout = QHBoxLayout(step_container)
        step_layout.setContentsMargins(5, 5, 5, 5)
        step_layout.setSpacing(8)

        step_button = QPushButton()
        step_button.setText(
            f"Шаг {step.num_in_form}\n"
            f"id:{step.num_in_form}\n"
            f"{step.target_point_name}"
        )
        step_button.setProperty("class", "step-button")

        step_button.setProperty("step_id", step.num_in_form)
        step_button.setProperty("num_in_form", step.num_in_form)
        step_button.clicked.connect(
            lambda checked, s=step, btn=step_button: self._on_step_clicked(s, btn)
        )

        step_layout.addWidget(step_button)

        tracks_container = QWidget()
        tracks_container.setProperty("class", "tracks-container")
        tracks_layout = QVBoxLayout(tracks_container)
        tracks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        tracks_layout.setContentsMargins(0, 0, 0, 0)
        tracks_layout.setSpacing(3)

        for track in step.r_tracks:
            self._add_track_widget(tracks_layout, track)

        step_layout.addWidget(tracks_container, 1)
        self.main_layout.addWidget(step_container)

    def _add_track_widget(self, parent_layout: QVBoxLayout, track: RTrack):
        """Добавляет виджет для трека"""
        track_wrapper = QWidget()
        track_wrapper.setProperty("class", "track-wrapper")
        track_layout = QHBoxLayout(track_wrapper)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(5)

        track_button = QPushButton(f"Трек {track.id}")
        track_button.setProperty("class", "track-button")

        track_button.setProperty("track_id", track.id)
        track_button.clicked.connect(
            lambda checked, t=track, btn=track_button: self._on_track_clicked(t, btn)
        )

        track_layout.addWidget(track_button)

        pazzles_container = QWidget()
        pazzles_container.setProperty("class", "pazzles-container")
        pazzles_layout = QHBoxLayout(pazzles_container)
        pazzles_layout.setContentsMargins(0, 0, 0, 0)
        pazzles_layout.setSpacing(3)
        pazzles_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for idx, sm in enumerate(track.rSM_objects):
            self._add_sm_widget(pazzles_layout, sm, idx)

        for ps in track.rPS_objects:
            self._add_ps_widget(pazzles_layout, ps)

        track_layout.addWidget(pazzles_container)
        parent_layout.addWidget(track_wrapper)

    def _add_sm_widget(self, parent_layout: QHBoxLayout, sm: R_SM, num_in_track: int):
        """Добавляет виджет для SM"""
        sm_button = QPushButton()

        class_name = sm.base_pazzle.class_ref.name
        if len(class_name) > 15:
            class_name = class_name[:12] + "..."

        sm_button.setText(
            f"SM{num_in_track}\n"
            f"id:{sm.base_pazzle.id}\n"
            f"{class_name}"
        )
        sm_button.setProperty("class", "sm-button")

        sm_button.setProperty("sm_id", sm.base_pazzle.id)
        sm_button.setProperty("num_in_track", num_in_track)
        sm_button.clicked.connect(
            lambda checked, s=sm, num=num_in_track, btn=sm_button: self._on_sm_clicked(s, num, btn)
        )

        parent_layout.addWidget(sm_button)

    def _add_ps_widget(self, parent_layout: QHBoxLayout, ps: R_PS):
        """Добавляет виджет для PS"""
        ps_button = QPushButton()

        class_name = ps.base_pazzle.class_ref.name
        if len(class_name) > 15:
            class_name = class_name[:12] + "..."

        ps_button.setText(
            f"PS\n"
            f"id:{ps.base_pazzle.id}\n"
            f"{class_name}"
        )
        ps_button.setProperty("class", "ps-button")

        ps_button.setProperty("ps_id", ps.base_pazzle.id)
        ps_button.clicked.connect(
            lambda checked, p=ps, btn=ps_button: self._on_ps_clicked(p, btn)
        )

        parent_layout.addWidget(ps_button)

    def _clear_layout(self, layout):
        """Очищает layout от всех виджетов"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _on_step_clicked(self, step: RStep, button: QPushButton):
        """Обработка клика по кнопке шага"""
        self._set_selected(button)
        self.signals.step_selected.emit(step.num_in_form, step.num_in_form)

    def _on_track_clicked(self, track: RTrack, button: QPushButton):
        """Обработка клика по кнопке трека"""
        self._set_selected(button)
        self.signals.track_selected.emit(track.id)

    def _on_sm_clicked(self, sm: R_SM, num_in_track: int, button: QPushButton):
        """Обработка клика по кнопке SM"""
        self._set_selected(button)
        self.signals.SM_selected.emit(sm.base_pazzle.id, num_in_track)

    def _on_ps_clicked(self, ps: R_PS, button: QPushButton):
        """Обработка клика по кнопке PS"""
        self._set_selected(button)
        self.signals.PS_selected.emit(ps.base_pazzle.id)

    def update_form(self, r_form: RForm):
        """Обновляет форму и перестраивает интерфейс"""
        self.r_form = r_form
        self.rsteps = r_form.rsteps
        self._build_structure()
        self.signals.form_updated.emit(r_form)

    def reload_styles(self) -> None:
        """Перезагружает стили"""
        self.apply_styles("id_selector.qss")

from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from CORE.run.r_form import RForm
from CORE.run.r_step import RStep
from CORE.run.r_track import RTrack
from CORE.run.r_sm import R_SM
from CORE.run.r_ps import R_PS
from DA3.base_widget import BaseWidget
from DA3.simulation_app.simulator_signals import get_signals


class IdSelector(BaseWidget):
    """Виджет для отображения и выбора шагов, треков, SM и PS"""

    def __init__(self, r_form: RForm, parent=None):
        super().__init__(parent)
        self.r_form = r_form
        self.rsteps: List[RStep] = r_form.rsteps

        # Получаем сигналы
        self.signals = get_signals()

        self._setup_ui()
        self._build_structure()

        # Применяем стили
        self.apply_styles("common.qss", "id_selector.qss")

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
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Убираем рамку скролла

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

        for step in self.rsteps:
            self._add_step_widget(step)

    def _add_step_widget(self, step: RStep):
        """Добавляет виджет для шага"""
        # Контейнер для шага с рамкой
        step_container = QFrame()
        step_container.setProperty("class", "step-container")
        step_container.setFrameShape(QFrame.Shape.StyledPanel)

        step_layout = QHBoxLayout(step_container)
        step_layout.setContentsMargins(5, 5, 5, 5)
        step_layout.setSpacing(8)

        # Кнопка шага
        step_button = QPushButton()
        step_button.setText(
            f"Шаг {step.num_in_form}\n"
            f"id:{step.num_in_form}\n"
            f"{step.target_point_name}"
        )
        step_button.setProperty("class", "id-selector-button step-button")

        # Сохраняем данные шага
        step_button.setProperty("step_id", step.num_in_form)
        step_button.setProperty("num_in_form", step.num_in_form)
        step_button.clicked.connect(
            lambda checked, s=step: self._on_step_clicked(s)
        )

        step_layout.addWidget(step_button)

        # Контейнер для треков
        tracks_container = QWidget()
        tracks_container.setProperty("class", "tracks-container")
        tracks_layout = QVBoxLayout(tracks_container)
        tracks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        tracks_layout.setContentsMargins(0, 0, 0, 0)
        tracks_layout.setSpacing(3)

        # Добавляем треки
        for track in step.r_tracks:
            self._add_track_widget(tracks_layout, track)

        step_layout.addWidget(tracks_container, 1)
        self.main_layout.addWidget(step_container)

    def _add_track_widget(self, parent_layout: QVBoxLayout, track: RTrack):
        """Добавляет виджет для трека"""
        # Контейнер для трека
        track_wrapper = QWidget()
        track_wrapper.setProperty("class", "track-wrapper")
        track_layout = QHBoxLayout(track_wrapper)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(5)

        # Кнопка трека
        track_button = QPushButton(f"Трек {track.id}")
        track_button.setProperty("class", "id-selector-button track-button")

        # Сохраняем данные трека
        track_button.setProperty("track_id", track.id)
        track_button.clicked.connect(
            lambda checked, t=track: self._on_track_clicked(t)
        )

        track_layout.addWidget(track_button)

        # Контейнер для SM и PS
        pazzles_container = QWidget()
        pazzles_container.setProperty("class", "pazzles-container")
        pazzles_layout = QHBoxLayout(pazzles_container)
        pazzles_layout.setContentsMargins(0, 0, 0, 0)
        pazzles_layout.setSpacing(3)
        pazzles_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Прижимаем к левому краю

        # Добавляем SM кнопки
        for idx, sm in enumerate(track.rSM_objects):
            self._add_sm_widget(pazzles_layout, sm, idx)

        # Добавляем PS кнопки
        for ps in track.rPS_objects:
            self._add_ps_widget(pazzles_layout, ps)

        track_layout.addWidget(pazzles_container)
        parent_layout.addWidget(track_wrapper)

    def _add_sm_widget(self, parent_layout: QHBoxLayout, sm: R_SM, num_in_track: int):
        """Добавляет виджет для SM"""
        sm_button = QPushButton()

        # Формируем текст с переносами строк
        class_name = sm.base_pazzle.class_ref.name
        if len(class_name) > 15:
            class_name = class_name[:12] + "..."

        sm_button.setText(
            f"SM{num_in_track}\n"
            f"id:{sm.base_pazzle.id}\n"
            f"{class_name}"
        )
        sm_button.setProperty("class", "id-selector-button sm-button")

        # Сохраняем данные SM
        sm_button.setProperty("sm_id", sm.base_pazzle.id)
        sm_button.setProperty("num_in_track", num_in_track)
        sm_button.clicked.connect(
            lambda checked, s=sm, num=num_in_track: self._on_sm_clicked(s, num)
        )

        parent_layout.addWidget(sm_button)

    def _add_ps_widget(self, parent_layout: QHBoxLayout, ps: R_PS):
        """Добавляет виджет для PS"""
        ps_button = QPushButton()

        # Формируем текст с переносами строк
        class_name = ps.base_pazzle.class_ref.name
        if len(class_name) > 15:
            class_name = class_name[:12] + "..."

        ps_button.setText(
            f"PS\n"
            f"id:{ps.base_pazzle.id}\n"
            f"{class_name}"
        )
        ps_button.setProperty("class", "id-selector-button ps-button")

        # Сохраняем данные PS
        ps_button.setProperty("ps_id", ps.base_pazzle.id)
        ps_button.clicked.connect(
            lambda checked, p=ps: self._on_ps_clicked(p)
        )

        parent_layout.addWidget(ps_button)

    def _clear_layout(self, layout):
        """Очищает layout от всех виджетов"""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _on_step_clicked(self, step: RStep):
        """Обработка клика по кнопке шага"""
        self.signals.step_selected.emit(step.num_in_form, step.num_in_form)

    def _on_track_clicked(self, track: RTrack):
        """Обработка клика по кнопке трека"""
        self.signals.track_selected.emit(track.id)

    def _on_sm_clicked(self, sm: R_SM, num_in_track: int):
        """Обработка клика по кнопке SM"""
        self.signals.SM_selected.emit(sm.base_pazzle.id, num_in_track)

    def _on_ps_clicked(self, ps: R_PS):
        """Обработка клика по кнопке PS"""
        self.signals.PS_selected.emit(ps.base_pazzle.id)

    def update_form(self, r_form: RForm):
        """Обновляет форму и перестраивает интерфейс"""
        self.r_form = r_form
        self.rsteps = r_form.rsteps
        self._build_structure()
        # Эмитируем сигнал об обновлении формы
        self.signals.form_updated.emit(r_form)

    def reload_styles(self) -> None:
        """Перезагружает стили"""
        self.apply_styles("common.qss", "id_selector.qss")
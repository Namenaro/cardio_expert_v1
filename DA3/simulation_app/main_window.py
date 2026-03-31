# DA3/simulation_app/main_window.py

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSplitter, QScrollArea, QFrame
)

from CORE.run.r_form import RForm
from DA3.simulation_app.content_manager import ContentManager
from DA3.simulation_app.simulation_widgets.dataset_navigator import DatasetNavigator
from DA3.simulation_app.simulation_widgets.id_selector import IdSelector
from DA3.simulation_app.simulator_signals import get_signals


class MainFormSimulator(QMainWindow):
    def __init__(self, r_form: Optional[RForm] = None, parent=None):
        super().__init__(parent)
        self.r_form = r_form
        self.form_name = r_form.form.name if r_form and hasattr(r_form, 'form') else "Неизвестная форма"

        # Получаем сигналы
        self.signals = get_signals()

        # Создаем менеджер контента
        self.content_manager = ContentManager(self)

        self._setup_ui()

        if self.r_form:
            self.update_form(self.r_form)

    def _setup_ui(self):
        self.setWindowTitle("Симулятор формы")
        self.setMinimumSize(1000, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Верхняя панель
        top_panel = QWidget()
        top_panel.setMaximumHeight(80)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)

        # Навигатор
        self.dataset_navigator = DatasetNavigator()
        top_layout.addWidget(self.dataset_navigator)

        # Название формы
        self.form_name_label = QLabel(f"Симулируемая форма: {self.form_name}")
        self.form_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_name_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #ccc;
            }
        """)
        top_layout.addWidget(self.form_name_label, 1)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Кнопка симуляции
        self.simulate_button = QPushButton("Полная симуляция")
        self.simulate_button.clicked.connect(self._on_simulate_clicked)
        buttons_layout.addWidget(self.simulate_button)

        # Кнопка снять выделение
        self.clear_selection_button = QPushButton("Снять выделение")
        self.clear_selection_button.clicked.connect(self._on_clear_selection_clicked)
        buttons_layout.addWidget(self.clear_selection_button)

        top_layout.addLayout(buttons_layout)

        main_layout.addWidget(top_panel)

        # Горизонтальный разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - селектор
        left_panel = self._create_selector_panel()
        splitter.addWidget(left_panel)

        # Правая панель - контент
        right_panel = self.content_manager.get_widget()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter, 1)

    def _create_selector_panel(self) -> QWidget:
        """Создает панель с селектором"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.selector_container = QWidget()
        self.selector_layout = QVBoxLayout(self.selector_container)
        self.selector_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(self.selector_container)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(scroll_area)

        return wrapper

    def update_form(self, r_form: RForm):
        """Обновляет форму"""
        self.r_form = r_form
        if hasattr(r_form, 'form') and hasattr(r_form.form, 'name'):
            self.form_name = r_form.form.name

        self.form_name_label.setText(f"Симулируемая форма: {self.form_name}")
        self._update_id_selector()

        # При смене формы очищаем правую панель
        self.content_manager.show_empty()

    def _update_id_selector(self):
        """Обновляет IdSelector"""
        while self.selector_layout.count():
            item = self.selector_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.r_form:
            self.id_selector = IdSelector(self.r_form)
            self.selector_layout.addWidget(self.id_selector)

    # Публичные методы для управления контентом
    def show_exemplar(self, exemplar, color='green'):
        """Показывает текущий экземпляр датасета"""
        self.content_manager.show_exemplar(exemplar, color)

    def show_track(self, track_res):
        """Показывает Track контент"""
        self.content_manager.show_track(track_res)

    def show_step(self, step_res):
        """Показывает Step контент"""
        self.content_manager.show_step(step_res)

    def show_empty(self, error_message=None):
        """Показывает пустой контент"""
        self.content_manager.show_empty(error_message)

    # Методы для управления навигатором
    def set_example_id(self, example_id: str) -> None:
        """Устанавливает ID примера в навигаторе"""
        if hasattr(self, 'dataset_navigator'):
            self.dataset_navigator.set_example_id(example_id)

    def get_example_id(self) -> str:
        """Возвращает текущий ID примера из навигатора"""
        if hasattr(self, 'dataset_navigator'):
            return self.dataset_navigator.get_example_id()
        return "—"

    def set_navigation_buttons_enabled(self, prev_enabled: bool, next_enabled: bool) -> None:
        """Устанавливает доступность кнопок навигации"""
        if hasattr(self, 'dataset_navigator'):
            self.dataset_navigator.set_buttons_enabled(prev_enabled, next_enabled)

    def _on_simulate_clicked(self):
        """Обработчик кнопки симуляции"""
        self.signals.full_simulate_requested.emit()

    def _on_clear_selection_clicked(self):
        """Обработчик кнопки снять выделение"""
        self.signals.clear_selection_requested.emit()

    def resizeEvent(self, event):
        """Обработка изменения размера"""
        super().resizeEvent(event)
        if hasattr(self, 'centralWidget'):
            for child in self.centralWidget().children():
                if isinstance(child, QSplitter):
                    total_width = child.width()
                    child.setSizes([int(total_width * 0.3), int(total_width * 0.7)])
                    break
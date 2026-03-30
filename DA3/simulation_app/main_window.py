from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSplitter, QScrollArea, QFrame, QHBoxLayout
)

from CORE.run.r_form import RForm
from DA3.simulation_app.simulation_widgets.id_selector import IdSelector
from DA3.simulation_app.simulation_widgets.dataset_navigator import DatasetNavigator


class MainFormSimulator(QMainWindow):
    def __init__(self, r_form: Optional[RForm] = None, parent=None):
        super().__init__(parent)
        self.r_form = r_form
        self.form_name = r_form.form.name if r_form and hasattr(r_form, 'form') else "Неизвестная форма"

        self._setup_ui()

        if self.r_form:
            self.update_form(self.r_form)

    def _setup_ui(self):
        self.setWindowTitle("Симулятор формы")
        self.setMinimumSize(1000, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout (вертикальный)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Верхняя панель - навигатор, название формы и кнопка в один ряд
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
        top_layout.addWidget(self.form_name_label, 1)  # Растягивается

        # Кнопка симуляции
        self.simulate_button = QPushButton("Полная симуляция")
        self.simulate_button.clicked.connect(self._on_simulate_clicked)
        top_layout.addWidget(self.simulate_button)

        main_layout.addWidget(top_panel)

        # Горизонтальный разделитель для левой и правой панели (основная часть)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - селектор с прокруткой
        left_panel = self._create_selector_panel()
        splitter.addWidget(left_panel)

        # Правая панель - пустой виджет
        right_panel = self._create_empty_panel()
        splitter.addWidget(right_panel)

        # Устанавливаем соотношение 30% на 70%
        splitter.setSizes([300, 700])

        # Splitter занимает всё оставшееся место
        main_layout.addWidget(splitter, 1)

    def _create_selector_panel(self) -> QWidget:
        """Создает панель с селектором и прокруткой"""
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

    def _create_empty_panel(self) -> QWidget:
        """Создает пустую правую панель"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_label = QLabel("Правая панель\n(пустой виджет)")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                font-style: italic;
            }
        """)
        layout.addWidget(info_label)

        return panel

    def update_form(self, r_form: RForm):
        """Обновляет форму и перестраивает интерфейс"""
        self.r_form = r_form
        if hasattr(r_form, 'form') and hasattr(r_form.form, 'name'):
            self.form_name = r_form.form.name

        self.form_name_label.setText(f"Симулируемая форма: {self.form_name}")

        self._update_id_selector()

    def _update_id_selector(self):
        """Обновляет виджет IdSelector"""
        while self.selector_layout.count():
            item = self.selector_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if self.r_form:
            self.id_selector = IdSelector(self.r_form)
            self.selector_layout.addWidget(self.id_selector)

    def _on_simulate_clicked(self):
        """Обработчик нажатия кнопки симуляции (пока пустой)"""
        pass

    def resizeEvent(self, event):
        """Обработка изменения размера окна для сохранения пропорций"""
        super().resizeEvent(event)
        if hasattr(self, 'centralWidget'):
            for child in self.centralWidget().children():
                if isinstance(child, QSplitter):
                    total_width = child.width()
                    child.setSizes([int(total_width * 0.3), int(total_width * 0.7)])
                    break